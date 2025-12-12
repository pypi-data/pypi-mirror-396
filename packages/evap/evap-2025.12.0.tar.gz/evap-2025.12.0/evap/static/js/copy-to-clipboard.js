export async function copyHeaders(headers) {
    await navigator.clipboard.writeText(headers.join("\t"));
}
