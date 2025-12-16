import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';
import { IEditorTracker, FileEditor } from '@jupyterlab/fileeditor';
import { IDocumentWidget } from '@jupyterlab/docregistry';
import {
  CodeMirrorEditor,
  IEditorExtensionRegistry,
  EditorExtensionRegistry
} from '@jupyterlab/codemirror';
import { EditorView, keymap } from '@codemirror/view';
import { Extension, Prec } from '@codemirror/state';
import {
  cursorSubwordForward,
  cursorSubwordBackward,
  cursorSyntaxLeft,
  cursorSyntaxRight,
  cursorGroupForward,
  cursorGroupBackward
} from '@codemirror/commands';
import {
  expandSelectionExtension,
  expandSelection,
  shrinkSelection,
  swapAnchorHead
} from 'codemirror-expand-selection';

function getActiveCodeMirrorEditor(
  app: JupyterFrontEnd,
  notebookTracker: INotebookTracker,
  editorTracker: IEditorTracker
): CodeMirrorEditor | null {
  let cm: CodeMirrorEditor | null = null;

  const widget = app.shell.currentWidget;
  if (!widget) {
    console.log('No widget');
    return cm;
  }

  if (notebookTracker.has(widget)) {
    // Notebook
    const panel = widget as NotebookPanel;
    const cell = panel.content.activeCell;
    if (cell && cell.editor instanceof CodeMirrorEditor) {
      cm = cell.editor as CodeMirrorEditor;
    }
  } else if (editorTracker.has(widget)) {
    // Editor
    const editorWidget = widget as IDocumentWidget<FileEditor>;
    const editor = editorWidget.content.editor;
    if (editor instanceof CodeMirrorEditor) {
      cm = editor as CodeMirrorEditor;
    }
  }
  return cm;
}

/**
 * Initialization data for the jupyterlab-expand-selection extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-expand-selection:plugin',
  description:
    'A JupyterLab extension that introduces expand/shrink selection commands',
  autoStart: true,
  requires: [INotebookTracker, IEditorTracker, IEditorExtensionRegistry],
  activate: (
    app: JupyterFrontEnd,
    notebookTracker: INotebookTracker,
    editorTracker: IEditorTracker,
    registry: IEditorExtensionRegistry
  ) => {
    console.log(
      'JupyterLab extension jupyterlab-expand-selection is activated!'
    );
    const overwriteKeymap = Prec.highest(
      keymap.of([
        { key: 'Alt-ArrowRight', run: cursorSubwordForward },
        { key: 'Alt-ArrowLeft', run: cursorSubwordBackward }
      ])
    );
    registry.addExtension(
      Object.freeze({
        name: 'jupyterlab-expand-selection:expand-selection-extension',
        default: { cyclic: true },
        factory: () =>
          EditorExtensionRegistry.createConfigurableExtension(
            (cfg: any) =>
              [expandSelectionExtension(cfg), overwriteKeymap] as Extension
          )
      })
    );
    app.commands.addCommand('jupyterlab-expand-selection:expand-selection', {
      label: 'Expand selected region',
      execute: () => {
        const cmEditor = getActiveCodeMirrorEditor(
          app,
          notebookTracker,
          editorTracker
        );
        if (!cmEditor) {
          console.warn('No active editor');
          return;
        }
        const view = cmEditor.editor as EditorView;
        expandSelection(view);
      }
    });

    app.commands.addCommand('jupyterlab-expand-selection:shrink-selection', {
      label: 'Shrink selected region',
      execute: () => {
        const cmEditor = getActiveCodeMirrorEditor(
          app,
          notebookTracker,
          editorTracker
        );
        if (!cmEditor) {
          console.warn('No active editor');
          return;
        }
        const view = cmEditor.editor as EditorView;
        shrinkSelection(view);
      }
    });

    app.commands.addCommand('jupyterlab-expand-selection:swap-anchor-head', {
      label: 'Swap anchor and head of the selected region',
      execute: () => {
        const cmEditor = getActiveCodeMirrorEditor(
          app,
          notebookTracker,
          editorTracker
        );
        if (!cmEditor) {
          console.warn('No active editor');
          return;
        }
        const view = cmEditor.editor as EditorView;
        swapAnchorHead(view);
      }
    });

    app.commands.addCommand('jupyterlab-expand-selection:subword-forward', {
      label: 'wrapper of codemirror cursorSubwordForward command',
      execute: () => {
        const cmEditor = getActiveCodeMirrorEditor(
          app,
          notebookTracker,
          editorTracker
        );
        if (!cmEditor) {
          console.warn('No active editor');
          return;
        }
        const view = cmEditor.editor as EditorView;
        cursorSubwordForward(view);
      }
    });

    app.commands.addCommand('jupyterlab-expand-selection:subword-backward', {
      label: 'Wrapper of codemirror cursorSubwordBackward command',
      execute: () => {
        const cmEditor = getActiveCodeMirrorEditor(
          app,
          notebookTracker,
          editorTracker
        );
        if (!cmEditor) {
          console.warn('No active editor');
          return;
        }
        const view = cmEditor.editor as EditorView;
        cursorSubwordBackward(view);
      }
    });

    app.commands.addCommand('jupyterlab-expand-selection:syntax-right', {
      label: 'wrapper of codemirror cursorSyntaxRight command',
      execute: () => {
        const cmEditor = getActiveCodeMirrorEditor(
          app,
          notebookTracker,
          editorTracker
        );
        if (!cmEditor) {
          console.warn('No active editor');
          return;
        }
        const view = cmEditor.editor as EditorView;
        cursorSyntaxRight(view);
      }
    });

    app.commands.addCommand('jupyterlab-expand-selection:syntax-left', {
      label: 'Wrapper of codemirror cursorSyntaxLeft command',
      execute: () => {
        const cmEditor = getActiveCodeMirrorEditor(
          app,
          notebookTracker,
          editorTracker
        );
        if (!cmEditor) {
          console.warn('No active editor');
          return;
        }
        const view = cmEditor.editor as EditorView;
        cursorSyntaxLeft(view);
      }
    });

    app.commands.addCommand('jupyterlab-expand-selection:group-forward', {
      label: 'Wrapper of codemirror cursorGroupForward command',
      execute: () => {
        const cmEditor = getActiveCodeMirrorEditor(
          app,
          notebookTracker,
          editorTracker
        );
        if (!cmEditor) {
          console.warn('No active editor');
          return;
        }
        const view = cmEditor.editor as EditorView;
        cursorGroupForward(view);
      }
    });

    app.commands.addCommand('jupyterlab-expand-selection:group-backward', {
      label: 'Wrapper of codemirror cursorGroupBackward command',
      execute: () => {
        const cmEditor = getActiveCodeMirrorEditor(
          app,
          notebookTracker,
          editorTracker
        );
        if (!cmEditor) {
          console.warn('No active editor');
          return;
        }
        const view = cmEditor.editor as EditorView;
        cursorGroupBackward(view);
      }
    });
  }
};

export default plugin;
