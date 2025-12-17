// Empty mock for modules not needed in RTL tests
class MockBlot {}
class MockContainer {}
class MockBlock {}
class MockInline {}
class MockEmbed {}

const mock = {
    import: (path) => {
        // Return mock classes for different Quill module paths
        if (path.includes('Container')) return MockContainer;
        if (path.includes('Block')) return MockBlock;
        if (path.includes('Inline')) return MockInline;
        if (path.includes('Embed')) return MockEmbed;
        return MockBlot;
    },
    register: () => {},
};

export default mock;
export const Delta = class {};
export const tableId = 'table';
