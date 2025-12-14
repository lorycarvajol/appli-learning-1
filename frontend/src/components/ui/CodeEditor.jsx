import { useState, useRef } from 'react';
import Editor from '@monaco-editor/react';
import './CodeEditor.css';

/**
 * CodeEditor - Composant d'éditeur de code basé sur Monaco Editor
 *
 * @param {string} value - Code actuel
 * @param {function} onChange - Callback appelé quand le code change
 * @param {string} language - Langage de programmation (html, css, javascript, python, etc.)
 * @param {number} height - Hauteur de l'éditeur en pixels (défaut: 400)
 * @param {string} theme - Thème de l'éditeur (vs-dark, vs-light)
 * @param {boolean} readOnly - Mode lecture seule
 * @param {object} options - Options supplémentaires pour Monaco
 */
export default function CodeEditor({
  value = '',
  onChange,
  language = 'html',
  height = 400,
  theme = 'vs-dark',
  readOnly = false,
  options = {},
}) {
  const editorRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);

  // Callback quand l'éditeur est monté
  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor;
    setIsLoading(false);

    // Configuration de l'auto-completion et autres features
    monaco.languages.html.htmlDefaults.setOptions({
      format: {
        tabSize: 2,
        insertSpaces: true,
      },
    });
  };

  // Callback quand le contenu change
  const handleEditorChange = (newValue) => {
    if (onChange) {
      onChange(newValue);
    }
  };

  // Options par défaut pour Monaco Editor
  const defaultOptions = {
    minimap: { enabled: false },
    fontSize: 14,
    lineNumbers: 'on',
    roundedSelection: false,
    scrollBeyondLastLine: false,
    automaticLayout: true,
    tabSize: 2,
    wordWrap: 'on',
    readOnly,
    suggestOnTriggerCharacters: true,
    quickSuggestions: true,
    parameterHints: { enabled: true },
    ...options,
  };

  return (
    <div className="code-editor">
      {isLoading && (
        <div className="code-editor__loading">
          <div className="loading-spinner"></div>
          <span>Chargement de l'éditeur...</span>
        </div>
      )}

      <Editor
        height={`${height}px`}
        language={language}
        theme={theme}
        value={value}
        onChange={handleEditorChange}
        onMount={handleEditorDidMount}
        options={defaultOptions}
        loading={null} // On gère le loading nous-mêmes
      />
    </div>
  );
}
