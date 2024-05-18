export function addStylesheetToDOM(cssFilePath: string) {
    // Create new link element
    let linkElement = document.createElement('link');

    // Set the relationship to 'stylesheet'
    linkElement.rel = 'stylesheet';

    // Set the href attribute to the given CSS file path
    linkElement.href = cssFilePath;

    // Append the link element to the head of the document
    document.head.appendChild(linkElement);
}