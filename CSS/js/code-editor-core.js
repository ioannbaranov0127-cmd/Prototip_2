/**
 * CodeMirror 6 — светлый Python-редактор для страницы обучения.
 */
import { EditorView, keymap, lineNumbers, highlightActiveLine, highlightActiveLineGutter, drawSelection } from '@codemirror/view';
import { EditorState } from '@codemirror/state';
import { defaultKeymap, history, historyKeymap, indentWithTab } from '@codemirror/commands';
import { python } from '@codemirror/lang-python';
import { syntaxHighlighting, indentOnInput, bracketMatching, HighlightStyle, indentUnit } from '@codemirror/language';
import { tags } from '@lezer/highlight';

var view = null;
var changeHandler = null;

var eduHighlight = HighlightStyle.define([
    { tag: tags.keyword, color: '#3d5a80', fontWeight: '600' },
    { tag: [tags.controlKeyword, tags.moduleKeyword], color: '#3d5a80', fontWeight: '600' },
    { tag: tags.operator, color: '#57606a' },
    { tag: tags.string, color: '#116329' },
    { tag: tags.number, color: '#0550ae' },
    { tag: tags.bool, color: '#0550ae' },
    { tag: tags.comment, color: '#6e7781', fontStyle: 'italic' },
    { tag: tags.function(tags.variableName), color: '#6f42c1' },
    { tag: tags.definition(tags.variableName), color: '#24292f' },
    { tag: tags.propertyName, color: '#24292f' },
    { tag: tags.punctuation, color: '#57606a' },
    { tag: tags.bracket, color: '#57606a' },
]);

var eduTheme = EditorView.theme(
    {
        '&': {
            fontSize: '13px',
            lineHeight: '1.55',
            backgroundColor: '#fff',
            color: '#24292f',
        },
        '&.cm-focused': {
            outline: 'none',
            boxShadow: 'inset 0 0 0 2px rgba(61, 90, 128, 0.15)',
        },
        '.cm-scroller': {
            fontFamily: 'var(--mono, "JetBrains Mono", Consolas, "Courier New", monospace)',
            overflow: 'auto',
            minHeight: '200px',
        },
        '.cm-content': {
            padding: '14px 16px',
            caretColor: '#24292f',
            minHeight: '200px',
        },
        '.cm-gutters': {
            backgroundColor: '#f8f9fb',
            color: '#9aa3ad',
            border: 'none',
            borderRight: '1px solid #e6e9ee',
            fontFamily: 'var(--mono, "JetBrains Mono", Consolas, "Courier New", monospace)',
            fontSize: '13px',
            lineHeight: '1.55',
        },
        '.cm-gutter.cm-lineNumbers .cm-gutterElement': {
            padding: '0 10px 0 0',
            minWidth: '28px',
        },
        '.cm-activeLineGutter': {
            backgroundColor: 'transparent',
            color: '#7a8490',
        },
        '.cm-activeLine': {
            backgroundColor: 'rgba(61, 90, 128, 0.04)',
        },
        '.cm-selectionBackground, &.cm-focused .cm-selectionBackground': {
            backgroundColor: 'rgba(61, 90, 128, 0.18) !important',
        },
        '.cm-cursor, .cm-dropCursor': {
            borderLeftColor: '#24292f',
        },
    },
    { dark: false }
);

function buildExtensions(onChange) {
    var extensions = [
        lineNumbers(),
        highlightActiveLine(),
        highlightActiveLineGutter(),
        drawSelection(),
        history(),
        indentOnInput(),
        bracketMatching(),
        syntaxHighlighting(eduHighlight, { fallback: true }),
        python(),
        indentUnit.of('    '),
        eduTheme,
        keymap.of([...defaultKeymap, ...historyKeymap, indentWithTab]),
        EditorView.domEventHandlers({
            keydown: function (event) {
                var mod = event.ctrlKey || event.metaKey;
                if (!mod) return false;
                var k = event.key.toLowerCase();
                if (k === 'z' || k === 'y') {
                    event.stopPropagation();
                }
                return false;
            },
        }),
    ];

    if (typeof onChange === 'function') {
        extensions.push(
            EditorView.updateListener.of(function (update) {
                if (update.docChanged) onChange();
            })
        );
    }

    return extensions;
}

function createState(doc) {
    return EditorState.create({
        doc: doc || '',
        extensions: buildExtensions(changeHandler),
    });
}

function destroyView() {
    if (view) {
        view.destroy();
        view = null;
    }
}

export function initLearnCodeEditor() {
    window.LearnCodeEditor = {
        create: function (mountEl, options) {
            if (!mountEl) return;
            options = options || {};
            destroyView();
            changeHandler = typeof options.onChange === 'function' ? options.onChange : null;
            mountEl.textContent = '';

            view = new EditorView({
                state: createState(options.initial != null ? options.initial : ''),
                parent: mountEl,
            });
        },

        destroy: destroyView,

        getValue: function () {
            return view ? view.state.doc.toString() : '';
        },

        setValue: function (text, resetHistory) {
            if (!view) return;
            var next = text != null ? String(text) : '';
            if (resetHistory) {
                view.setState(createState(next));
            } else {
                view.dispatch({
                    changes: { from: 0, to: view.state.doc.length, insert: next },
                });
            }
        },

        focus: function () {
            if (view) view.focus();
        },
    };

    window.dispatchEvent(new Event('learn-code-editor-ready'));
}
