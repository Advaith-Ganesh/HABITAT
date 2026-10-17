import js from "@eslint/js";
import tseslint from "typescript-eslint";
import hooks from "eslint-plugin-react-hooks";
export default tseslint.config(
  { ignores: ["dist"] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["src/**/*.{ts,tsx}"],
    languageOptions: {
      globals: {
        window: "readonly",
        document: "readonly",
        localStorage: "readonly",
        history: "readonly",
        location: "readonly",
        fetch: "readonly",
        AbortSignal: "readonly",
        DOMException: "readonly",
        URLSearchParams: "readonly",
        KeyboardEvent: "readonly",
        FormEvent: "readonly",
        HTMLDialogElement: "readonly",
        HTMLFormElement: "readonly",
      },
    },
    plugins: { "react-hooks": hooks },
    rules: {
      ...hooks.configs.recommended.rules,
      "@typescript-eslint/no-explicit-any": "off",
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_" },
      ],
    },
  },
);
