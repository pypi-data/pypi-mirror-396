import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';

import { PageConfig } from '@jupyterlab/coreutils';

const TRACKING_KEY = 'tracking';

/**
 * A history record entry saved on each notebook save.
 */
interface HistoryRecord {
  timestamp: string;
  user: string;
  bytes: number;
  edit_time_seconds: number;
  [key: string]: string | number;
}

/**
 * The tracking metadata structure stored under notebook.metadata.tracking
 */
interface TrackingMetadata {
  total_edit_time_seconds: number;
  last_edit_by?: string;
  editors: Record<string, number>;
  history: HistoryRecord[];
  [key: string]: string | number | Record<string, number> | HistoryRecord[] | undefined;
}

/**
 * Track editing time for a single notebook panel.
 */
class NotebookEditTimeTracker {
  private _panel: NotebookPanel;
  private _sessionStartTime: number | null = null;

  constructor(panel: NotebookPanel) {
    this._panel = panel;

    // Start tracking when the notebook becomes ready
    panel.context.ready.then(() => {
      this._startSession();
    });

    // When notebook is about to save, update the edit time
    panel.context.saveState.connect(this._onSaveState, this);

    // Clean up when panel is disposed
    panel.disposed.connect(() => {
      panel.context.saveState.disconnect(this._onSaveState, this);
    });
  }

  private _startSession(): void {
    this._sessionStartTime = Date.now();
  }

  private _onSaveState = (
    _: any,
    state: 'started' | 'completed' | 'failed'
  ): void => {
    if (state === 'started' && this._sessionStartTime !== null) {
      this._updateEditTime();
    }
  };

  private _updateEditTime(): void {
    if (this._sessionStartTime === null) {
      return;
    }

    const model = this._panel.context.model;
    if (!model) {
      return;
    }

    const now = Date.now();
    const elapsedSeconds = Math.floor((now - this._sessionStartTime) / 1000);

    // Get current tracking metadata, or initialize with defaults
    const metadata = model.sharedModel.metadata;
    const tracking: TrackingMetadata = (metadata[TRACKING_KEY] as TrackingMetadata) || {
      total_edit_time_seconds: 0,
      editors: {},
      history: []
    };

    // Add elapsed time to total
    tracking.total_edit_time_seconds += elapsedSeconds;

    // Get the current user from JUPYTERHUB_USER (available via hubUser in PageConfig)
    const hubUser = PageConfig.getOption('hubUser');
    if (hubUser) {
      // Set last_edit_by
      tracking.last_edit_by = hubUser;

      // Update editors dictionary with per-user edit time
      const userEditTime = tracking.editors[hubUser] || 0;
      tracking.editors[hubUser] = userEditTime + elapsedSeconds;
    }

    // Append a history record
    const notebookContent = JSON.stringify(model.sharedModel.toJSON());
    const byteSize = new TextEncoder().encode(notebookContent).length;
    const historyRecord: HistoryRecord = {
      timestamp: new Date().toISOString(),
      user: hubUser || 'unknown',
      bytes: byteSize,
      edit_time_seconds: elapsedSeconds
    };
    tracking.history.push(historyRecord);

    // Save the tracking metadata
    model.sharedModel.setMetadata(TRACKING_KEY, tracking);

    // Reset session start time to now (so we track time since last save)
    this._sessionStartTime = now;
  }
}

/**
 * Initialization data for the jupyter_notebook_tracking extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyter_notebook_tracking:plugin',
  description: 'Track total editing time in Jupyter notebooks',
  autoStart: true,
  requires: [INotebookTracker],
  activate: (app: JupyterFrontEnd, notebookTracker: INotebookTracker) => {
    console.log(
      'JupyterLab extension jupyter_notebook_tracking is activated!'
    );

    // Track edit time for each notebook that is opened
    notebookTracker.widgetAdded.connect((_, panel: NotebookPanel) => {
      new NotebookEditTimeTracker(panel);
    });
  }
};

export default plugin;
