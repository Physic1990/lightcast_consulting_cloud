# Frontend Files

## Features

This frontend uses Yarn for package management and Vite as a development server. It displays information gathered from the backend - primarily Google Drive files and local Python scripts - and allows the user to navigate through them and send operations to the backend and eventually the local helper.

## Key File Structure

/src/: Contains all TypeScript and design files - root source code directory.<br>
/src/assets/: Contains images for display in the application itself.<br>
/src/components/: Contains TypeScript code for individual React components/display features.<br>
/src/types.ts: Definitions for custom types in the application.

## Run Dev Build

Prerequisite: install [yarn](https://yarnpkg.com/)

From the frontend directory, run:

```bash
yarn install
yarn run dev
```

To add dependencies to the project, run:

```bash
yarn add <package-name>
```

The frontend will be available at http://localhost:3000.
