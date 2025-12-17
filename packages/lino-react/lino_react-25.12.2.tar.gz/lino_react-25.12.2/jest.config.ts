import type { Config } from 'jest';

// https://jestjs.io/docs/configuration
const config: Config = {
    // bail: true, // bail after first failure
    globalSetup: "<rootDir>/lino_react/react/testSetup/setupJEST.js",
    globalTeardown: "<rootDir>/lino_react/react/testSetup/teardownJEST.js",
    testEnvironment: process.env.BABEL === '1' ? 'jsdom' : "<rootDir>/lino_react/react/testSetup/testEnvironment.js",
    moduleFileExtensions: ["js", "jsx", "ts", "tsx"],
    moduleNameMapper: {
        '^.+\\.(css|less)$': '<rootDir>/CSSStub.js',
        '^quill$': '<rootDir>/lino_react/react/testSetup/mocks/emptyMock.js',
        '^quill-next-react$': '<rootDir>/lino_react/react/testSetup/mocks/emptyMock.js',
        '^quill-image-drop-and-paste$': '<rootDir>/lino_react/react/testSetup/mocks/emptyMock.js',
        '^@enzedonline/quill-blot-formatter2$': '<rootDir>/lino_react/react/testSetup/mocks/emptyMock.js',
        '^quill-html-edit-button$': '<rootDir>/lino_react/react/testSetup/mocks/emptyMock.js',
        '^quill-mention$': '<rootDir>/lino_react/react/testSetup/mocks/quillMentionMock.js',
        '^@mswjs/interceptors/(.*)$': '<rootDir>/node_modules/@mswjs/interceptors/$1',
        '^msw/node$': '<rootDir>/node_modules/msw/lib/node/index.js',
    },
    preset: 'jest-puppeteer',
    // testRegex: "(/__tests__/.*|(\\.|/)(test|spec))\\.(jsx?|tsx?|js?|ts?)$",
    roots: ["<rootDir>/lino_react/react/components"],
    setupFilesAfterEnv: ["<rootDir>/lino_react/react/testSetup/setupTests.ts"],
    testMatch: [`<rootDir>/lino_react/react/components/__tests__/${process.env.BASE_SITE}/*.ts${process.env.BABEL ? 'x' : ''}`],
    testTimeout: 300000,
    transform: {
        '^.+\\.(ts|tsx)?$': 'ts-jest',
        '^.+\\.(js|jsx)$': 'babel-jest',
    },
    transformIgnorePatterns: [
        "node_modules/(?!(query-string|decode-uri-component|split-on-first|filter-obj|quill|quill-next-react|lodash-es|parchment|quill-mention|quill-html-edit-button|quill-image-drop-and-paste|@enzedonline|msw|@mswjs|until-async)/)"
    ],
    verbose: true,
}

export default config;
