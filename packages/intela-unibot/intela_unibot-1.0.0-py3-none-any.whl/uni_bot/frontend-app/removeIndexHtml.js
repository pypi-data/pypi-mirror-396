import { unlink } from 'fs/promises';
import { resolve } from 'path';


const filePath = resolve('dist', 'uni_bot', 'index.html');

async function removeFile() {
  try {
    await unlink(filePath);
    // eslint-disable-next-line no-console
    console.log('The index.html in the dist folder has been deleted.');
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('Error deleting index.html in dist folder:', err);
  }
}

removeFile();
