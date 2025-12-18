import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { IDefaultFileBrowser } from '@jupyterlab/filebrowser';
import { ILauncher } from '@jupyterlab/launcher';
import { ITerminalTracker } from '@jupyterlab/terminal';
import { showErrorMessage } from '@jupyterlab/apputils';
import { ServerConnection } from '@jupyterlab/services';
import { URLExt, PageConfig } from '@jupyterlab/coreutils';

/**
 * Command IDs for the extension.
 */
const SHOW_IN_BROWSER_CMD = 'launcher:show-kernel-in-file-browser';
const OPEN_TERMINAL_CMD = 'launcher:open-terminal-at-kernel';
const UNREGISTER_KERNEL_CMD = 'launcher:unregister-venv-kernel';

/**
 * Interface for the kernel path API response.
 */
interface IKernelPathResponse {
  kernel_name: string;
  display_name: string;
  resource_dir: string;
  executable_path: string | null;
  env_path: string | null;
  error?: string;
}

/**
 * Interface for nb_venv_kernels environment entry.
 */
interface IVenvEnvironment {
  name: string;
  custom_name: string | null;
  type: string;
  exists: boolean;
  has_kernel: boolean;
  path: string;
}

/**
 * Interface for nb_venv_kernels environments list response.
 */
interface IVenvEnvironmentsResponse {
  environments: IVenvEnvironment[];
  workspace_root: string;
}

/**
 * Interface for nb_venv_kernels unregister response.
 */
interface IUnregisterResponse {
  success: boolean;
  message?: string;
  error?: string;
}

/**
 * Store for the last right-clicked kernel display name.
 * This is set when a context menu is opened on a launcher card.
 */
let lastClickedKernelName: string | null = null;

/**
 * Flag indicating whether nb_venv_kernels extension is available.
 * Checked once at startup.
 */
let nbVenvKernelsAvailable = false;

/**
 * Fetch the kernel path information from the server.
 *
 * @param displayName - The display name of the kernel
 * @returns Promise resolving to kernel path info or null if not available
 */
async function fetchKernelPath(
  displayName: string
): Promise<IKernelPathResponse | null> {
  const settings = ServerConnection.makeSettings();
  const url = URLExt.join(
    settings.baseUrl,
    'api',
    'kernel-path',
    encodeURIComponent(displayName)
  );

  try {
    const response = await ServerConnection.makeRequest(url, {}, settings);

    if (!response.ok) {
      const data = (await response.json()) as IKernelPathResponse;
      console.warn(`Failed to get kernel path: ${data.error}`);
      return null;
    }

    const data = (await response.json()) as IKernelPathResponse;
    return data;
  } catch (error) {
    console.error('Error fetching kernel path:', error);
    return null;
  }
}

/**
 * Check if nb_venv_kernels extension is available.
 *
 * @returns Promise resolving to true if available, false otherwise
 */
async function checkNbVenvKernelsAvailable(): Promise<boolean> {
  const settings = ServerConnection.makeSettings();
  const url = URLExt.join(settings.baseUrl, 'nb-venv-kernels', 'environments');

  try {
    const response = await ServerConnection.makeRequest(url, {}, settings);
    return response.ok;
  } catch (error) {
    console.debug('nb_venv_kernels extension not installed:', error);
    return false;
  }
}

/**
 * Fetch list of venv environments from nb_venv_kernels API.
 *
 * @returns Promise resolving to environments list or null if not available
 */
async function fetchVenvEnvironments(): Promise<IVenvEnvironmentsResponse | null> {
  const settings = ServerConnection.makeSettings();
  const url = URLExt.join(settings.baseUrl, 'nb-venv-kernels', 'environments');

  try {
    const response = await ServerConnection.makeRequest(url, {}, settings);

    if (!response.ok) {
      console.warn('nb_venv_kernels API not available');
      return null;
    }

    const data = (await response.json()) as IVenvEnvironmentsResponse;
    return data;
  } catch (error) {
    console.debug('nb_venv_kernels extension not installed:', error);
    return null;
  }
}

/**
 * Find a venv environment matching the given display name.
 *
 * @param displayName - The kernel display name to match
 * @returns The matching environment or null
 */
async function findVenvEnvironment(
  displayName: string
): Promise<IVenvEnvironment | null> {
  const envData = await fetchVenvEnvironments();
  if (!envData) {
    return null;
  }

  // Find matching environment by name
  // Display name patterns: "Python (envname)", "envname", "Python 3 (envname)"
  for (const env of envData.environments) {
    // Skip conda environments - they can't be unregistered via nb_venv_kernels
    if (env.type === 'conda') {
      continue;
    }

    const envName = env.name || '';
    const customName = env.custom_name || '';

    // Check if display_name contains the environment name
    if (
      (envName && displayName.includes(envName)) ||
      (customName && displayName.includes(customName))
    ) {
      return env;
    }
  }

  return null;
}

/**
 * Unregister a venv environment via nb_venv_kernels API.
 *
 * @param envPath - The path of the environment to unregister
 * @returns Promise resolving to unregister result
 */
async function unregisterVenvKernel(
  envPath: string
): Promise<IUnregisterResponse> {
  const settings = ServerConnection.makeSettings();
  const url = URLExt.join(settings.baseUrl, 'nb-venv-kernels', 'unregister');

  try {
    const response = await ServerConnection.makeRequest(
      url,
      {
        method: 'POST',
        body: JSON.stringify({ path: envPath })
      },
      settings
    );

    const data = (await response.json()) as IUnregisterResponse;

    if (!response.ok) {
      return {
        success: false,
        error: data.error || 'Failed to unregister kernel'
      };
    }

    return { success: true, message: data.message };
  } catch (error) {
    console.error('Error unregistering kernel:', error);
    return {
      success: false,
      error: `Network error: ${error}`
    };
  }
}

/**
 * Expand tilde in path using the home directory extracted from absolutePath.
 *
 * @param path - Path that may contain ~
 * @param absolutePath - An absolute path to extract home directory from
 * @returns Path with ~ expanded, or original if expansion not possible
 */
function expandTilde(path: string, absolutePath: string): string {
  if (!path.startsWith('~')) {
    return path;
  }

  // Extract home directory from absolute path
  // Matches /home/username or /Users/username
  const match = absolutePath.match(/^(\/(?:home|Users)\/[^/]+)/);
  if (!match) {
    return path;
  }

  const homedir = match[1];
  if (path === '~') {
    return homedir;
  }
  if (path.startsWith('~/')) {
    return homedir + path.slice(1);
  }
  return path;
}

/**
 * Convert an absolute filesystem path to a path relative to the server root.
 *
 * @param absolutePath - The absolute filesystem path
 * @param serverRoot - The server's root directory (may contain ~)
 * @returns The relative path for the file browser, or null if outside server root
 */
function toRelativePath(
  absolutePath: string,
  serverRoot: string
): string | null {
  // Normalize path - ensure no trailing slashes
  const normalizedPath = absolutePath.replace(/\/+$/, '');

  // Expand tilde in serverRoot and normalize
  const normalizedRoot = expandTilde(serverRoot, absolutePath).replace(
    /\/+$/,
    ''
  );

  // Check if path is the server root
  if (normalizedPath === normalizedRoot) {
    return '';
  }

  // Check if path is inside the server root
  const rootPrefix = normalizedRoot + '/';
  if (normalizedPath.startsWith(rootPrefix)) {
    return normalizedPath.slice(rootPrefix.length);
  }

  // Path is outside the server root
  return null;
}

/**
 * Extract kernel display name from a launcher card element.
 *
 * @param element - The clicked element or its parent launcher card
 * @returns The kernel display name or null if not found
 */
function extractKernelNameFromCard(element: HTMLElement): string | null {
  // Find the launcher card (might be the element itself or a parent)
  const card = element.closest('.jp-LauncherCard') as HTMLElement | null;
  if (!card) {
    return null;
  }

  // Find the label element within the card
  const label = card.querySelector('.jp-LauncherCard-label');
  if (label && label.textContent) {
    return label.textContent.trim();
  }

  // Fallback: try the title attribute
  if (card.title) {
    return card.title;
  }

  return null;
}

/**
 * Setup event listener to capture right-clicked kernel name.
 */
function setupContextMenuCapture(): void {
  document.addEventListener(
    'contextmenu',
    (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (target) {
        const card = target.closest('.jp-LauncherCard');
        if (card) {
          lastClickedKernelName = extractKernelNameFromCard(target);
        }
      }
    },
    true
  ); // Use capture phase to get event before context menu
}

/**
 * Initialization data for the jupyterlab_launcher_navigate_to_kernel_extension extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab_launcher_navigate_to_kernel_extension:plugin',
  description:
    "Right-click kernel launcher cards to navigate file browser to kernel's location or open terminal there",
  autoStart: true,
  requires: [IDefaultFileBrowser],
  optional: [ILauncher, ITerminalTracker],
  activate: (
    app: JupyterFrontEnd,
    fileBrowser: IDefaultFileBrowser,
    launcher: ILauncher | null,
    terminalTracker: ITerminalTracker | null
  ) => {
    console.log(
      'JupyterLab extension jupyterlab_launcher_navigate_to_kernel_extension is activated!'
    );

    const { commands } = app;

    // Get the server root directory from PageConfig
    const serverRoot = PageConfig.getOption('serverRoot');

    // Setup event listener to capture kernel name on right-click
    setupContextMenuCapture();

    // Check if nb_venv_kernels is available (for unregister feature)
    checkNbVenvKernelsAvailable().then(available => {
      nbVenvKernelsAvailable = available;
      if (available) {
        console.log('nb_venv_kernels extension detected - unregister feature enabled');
      }
    });

    // Add the "Show in File Browser" command
    commands.addCommand(SHOW_IN_BROWSER_CMD, {
      label: 'Show in File Browser',
      caption: "Navigate file browser to kernel's directory",
      isEnabled: () => lastClickedKernelName !== null,
      execute: async () => {
        if (!lastClickedKernelName) {
          await showErrorMessage(
            'No Kernel Selected',
            'Could not determine which kernel was selected.'
          );
          return;
        }

        const kernelInfo = await fetchKernelPath(lastClickedKernelName);

        if (!kernelInfo) {
          await showErrorMessage(
            'Kernel Not Found',
            `Could not find path information for kernel "${lastClickedKernelName}".`
          );
          return;
        }

        // Prefer env_path (conda environment) if available, otherwise use resource_dir
        const targetPath = kernelInfo.env_path || kernelInfo.resource_dir;

        // Convert to relative path for file browser
        const relativePath = toRelativePath(targetPath, serverRoot);

        // If outside workspace, fallback to workspace root
        const navigatePath = relativePath === null ? '' : relativePath;

        try {
          const absolutePath = navigatePath === '' ? '/' : '/' + navigatePath;
          await fileBrowser.model.cd(absolutePath);
        } catch (error) {
          console.error('Failed to navigate file browser:', error);
          await showErrorMessage(
            'Navigation Error',
            `Failed to navigate to: ${targetPath}\nError: ${error}`
          );
        }
      }
    });

    // Add the "Open Terminal at location" command
    commands.addCommand(OPEN_TERMINAL_CMD, {
      label: 'Open Terminal at Location',
      caption: "Open a terminal at the kernel's directory",
      isEnabled: () =>
        lastClickedKernelName !== null && terminalTracker !== null,
      execute: async () => {
        if (!lastClickedKernelName) {
          await showErrorMessage(
            'No Kernel Selected',
            'Could not determine which kernel was selected.'
          );
          return;
        }

        const kernelInfo = await fetchKernelPath(lastClickedKernelName);

        if (!kernelInfo) {
          await showErrorMessage(
            'Kernel Not Found',
            `Could not find path information for kernel "${lastClickedKernelName}".`
          );
          return;
        }

        // Prefer env_path (conda environment) if available, otherwise use resource_dir
        const targetPath = kernelInfo.env_path || kernelInfo.resource_dir;

        // Convert to relative path for terminal (terminal:create-new requires relative path)
        const relativePath = toRelativePath(targetPath, serverRoot);

        // If outside workspace, use empty string (workspace root)
        const terminalCwd = relativePath === null ? '' : relativePath;

        try {
          // Open a new terminal with relative path
          await commands.execute('terminal:create-new', {
            cwd: terminalCwd
          });
        } catch (error) {
          console.error('Failed to open terminal:', error);
          await showErrorMessage(
            'Terminal Error',
            `Failed to open terminal at: ${targetPath}\nError: ${error}`
          );
        }
      }
    });

    // Add the "Unregister Kernel" command (shown when nb_venv_kernels is available)
    commands.addCommand(UNREGISTER_KERNEL_CMD, {
      label: 'Unregister Kernel',
      caption: 'Remove this kernel from nb_venv_kernels registry',
      isEnabled: () => lastClickedKernelName !== null && nbVenvKernelsAvailable,
      isVisible: () => nbVenvKernelsAvailable,
      execute: async () => {
        if (!lastClickedKernelName) {
          await showErrorMessage(
            'No Kernel Selected',
            'Could not determine which kernel was selected.'
          );
          return;
        }

        // Find the venv environment for this kernel
        const env = await findVenvEnvironment(lastClickedKernelName);

        if (!env) {
          await showErrorMessage(
            'Cannot Unregister',
            `"${lastClickedKernelName}" is not managed by nb_venv_kernels.`
          );
          return;
        }

        // Unregister the kernel
        const result = await unregisterVenvKernel(env.path);

        if (result.success) {
          console.log(`Kernel unregistered: ${env.path}`);
          await showErrorMessage(
            'Kernel Unregistered',
            `Successfully unregistered "${env.name}" (${env.path}).\n\nTo re-register this environment, use:\n  nb_venv_kernels register ${env.path}`
          );
        } else {
          await showErrorMessage(
            'Unregister Failed',
            `Failed to unregister kernel: ${result.error}`
          );
        }
      }
    });

    console.log(
      `Commands registered: ${SHOW_IN_BROWSER_CMD}, ${OPEN_TERMINAL_CMD}, ${UNREGISTER_KERNEL_CMD}`
    );
  }
};

export default plugin;
