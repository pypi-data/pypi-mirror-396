import {
  EditorState,
  EditorView,
  HighlightStyle,
  LanguageSupport,
  StreamLanguage,
  base_extensions,
  keymap,
  placeholder,
  replace_contents,
  syntaxHighlighting,
  tags
} from "./chunk-YR5BHN2B.js";

// src/codemirror/bql-highlight.ts
var bql_highlight = HighlightStyle.define([
  {
    // Keywords: Select, Where, And
    tag: tags.keyword,
    color: "var(--bql-keywords)"
  },
  {
    // Values
    tag: [
      tags.typeName,
      tags.className,
      tags.number,
      tags.changed,
      tags.annotation,
      tags.modifier,
      tags.self,
      tags.namespace
    ],
    color: "var(--bql-values)"
  },
  {
    // Strings
    tag: [tags.processingInstruction, tags.string, tags.inserted],
    color: "var(--bql-string)"
  },
  {
    // Errors
    tag: [
      tags.name,
      tags.deleted,
      tags.character,
      tags.propertyName,
      tags.macroName
    ],
    color: "var(--bql-errors)"
  }
]);

// src/codemirror/bql-grammar.ts
var bql_grammar_default = {
  columns: [
    "account",
    "accounts",
    "amount",
    "balance",
    "close",
    "comment",
    "cost_currency",
    "cost_date",
    "cost_label",
    "cost_number",
    "currency",
    "date",
    "day",
    "description",
    "discrepancy",
    "entry",
    "filename",
    "flag",
    "id",
    "lineno",
    "links",
    "location",
    "meta",
    "month",
    "name",
    "narration",
    "number",
    "open",
    "other_accounts",
    "payee",
    "position",
    "posting_flag",
    "price",
    "tags",
    "tolerance",
    "type",
    "weight",
    "year"
  ],
  functions: [
    "abs",
    "account_sortkey",
    "any_meta",
    "bool",
    "close_date",
    "commodity",
    "commodity_meta",
    "convert",
    "cost",
    "count",
    "currency",
    "currency_meta",
    "date",
    "date_add",
    "date_bin",
    "date_diff",
    "date_part",
    "date_trunc",
    "day",
    "decimal",
    "empty",
    "entry_meta",
    "filter_currency",
    "findfirst",
    "first",
    "getitem",
    "getprice",
    "grep",
    "grepn",
    "has_account",
    "int",
    "interval",
    "joinstr",
    "last",
    "leaf",
    "length",
    "lower",
    "max",
    "maxwidth",
    "meta",
    "min",
    "month",
    "neg",
    "number",
    "only",
    "open_date",
    "open_meta",
    "parent",
    "parse_date",
    "possign",
    "quarter",
    "repr",
    "root",
    "round",
    "safediv",
    "splitcomp",
    "str",
    "subst",
    "substr",
    "sum",
    "today",
    "units",
    "upper",
    "value",
    "weekday",
    "year",
    "yearmonth"
  ],
  keywords: [
    "and",
    "as",
    "asc",
    "balances",
    "by",
    "create",
    "desc",
    "distinct",
    "false",
    "from",
    "group",
    "having",
    "in",
    "insert",
    "into",
    "is",
    "journal",
    "limit",
    "not",
    "or",
    "order",
    "pivot",
    "print",
    "select",
    "table",
    "true",
    "using",
    "where"
  ]
};

// src/codemirror/bql-autocomplete.ts
var { columns, functions, keywords } = bql_grammar_default;
var columns_functions_keywords = [
  ...columns,
  ...functions.map((f) => `${f}(`),
  ...keywords
].map((label) => ({ label }));
var command_completions = [
  "balances",
  "errors",
  "explain",
  "help",
  "lex",
  "parse",
  "print",
  "runcustom",
  "select",
  "tokenize"
].map((label) => ({ label }));
var bql_completion = (context) => {
  const token = context.matchBefore(/\w+/);
  if (!token) {
    return null;
  }
  if (token.from === 0) {
    return { from: token.from, options: command_completions };
  }
  return { from: token.from, options: columns_functions_keywords };
};

// src/codemirror/bql-stream-parser.ts
var keywords2 = new Set(bql_grammar_default.keywords);
var columns2 = new Set(bql_grammar_default.columns);
var functions2 = new Set(bql_grammar_default.functions);
var string = /^("[^"]*"|'[^']*')/;
var date = /^(?:#(?:"[^"]*"|'[^']*')|\d\d\d\d-\d\d-\d\d)/;
var decimal = /^[-+]?([0-9]+\.[0-9]*|[0-9]*\.[0-9]+)/;
var integer = /^[-+]?[0-9]+/;
var m = (s, p) => {
  const match = s.match(p);
  return match != null && match !== false;
};
var bql_stream_parser = {
  token(stream) {
    if (stream.eatSpace() || stream.eol()) {
      return null;
    }
    if (m(stream, string)) {
      return "string";
    }
    if (m(stream, date) || m(stream, decimal) || m(stream, integer)) {
      return "number";
    }
    if (m(stream, /\w+/)) {
      const word = stream.current().toLowerCase();
      if (keywords2.has(word)) {
        return "keyword";
      }
      if (columns2.has(word)) {
        return "typeName";
      }
      if (functions2.has(word) && stream.peek() === "(") {
        return "macroName";
      }
      return "name";
    }
    const char = stream.next();
    if (char === "*") {
      return "typeName";
    }
    return null;
  }
};

// src/codemirror/bql-language.ts
var bql_language = StreamLanguage.define(bql_stream_parser);
var bql_language_support = new LanguageSupport(
  bql_language,
  bql_language.data.of({
    autocomplete: bql_completion
  })
);

// src/codemirror/bql.ts
function init_document_preview_editor() {
  return new EditorView({
    extensions: [
      base_extensions,
      EditorState.readOnly.of(true),
      placeholder("Loading...")
    ]
  });
}
function init_readonly_query_editor(value) {
  return new EditorView({
    doc: value,
    extensions: [
      bql_language_support,
      syntaxHighlighting(bql_highlight),
      EditorState.readOnly.of(true)
    ]
  });
}
function init_query_editor(value, onDocChanges, placeholder_value, get_submit) {
  return new EditorView({
    doc: value,
    extensions: [
      bql_language_support,
      EditorView.updateListener.of((update) => {
        if (update.docChanged) {
          onDocChanges(update.state);
        }
      }),
      keymap.of([
        {
          key: "Control-Enter",
          mac: "Meta-Enter",
          run: () => {
            const submit = get_submit();
            submit();
            return true;
          }
        }
      ]),
      placeholder(placeholder_value),
      base_extensions,
      syntaxHighlighting(bql_highlight)
    ]
  });
}
export {
  init_document_preview_editor,
  init_query_editor,
  init_readonly_query_editor,
  replace_contents
};
//# sourceMappingURL=bql-6CKHT46Q.js.map
