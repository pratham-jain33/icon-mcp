# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

Only the latest minor release line receives security fixes.

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Instead, email **hello@prathamjain.com** with:

- a description of the vulnerability,
- steps to reproduce it,
- the version you tested against.

You can expect an acknowledgement within 7 days. If the issue is confirmed,
a fix will be released and credited in the release notes (unless you ask to
stay anonymous).

## Scope notes

- This server is **fully offline**: it bundles the Lucide icon set locally
  and generates SVGs on your machine. It makes no network requests and needs
  no API keys.
- Generated SVGs are derived from the ISC-licensed Lucide icons; keep the
  license attribution when redistributing them.
