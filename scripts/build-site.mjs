import { access, copyFile, mkdir, rm, stat } from 'node:fs/promises';
import { resolve, join } from 'node:path';

// Build a verified static distribution of the Parts Unlimited demo site.
const source = resolve('docs');
const destination = resolve('dist');
const requiredFiles = ['index.html', 'styles.css', 'catalog.mjs', 'site.mjs'];

for (const file of requiredFiles) {
  const filepath = join(source, file);
  await access(filepath);
  if (!(await stat(filepath)).isFile()) {
    throw new Error(`Not a regular file: ${filepath}`);
  }
}

await rm(destination, { recursive: true, force: true });
await mkdir(destination, { recursive: true });
for (const file of requiredFiles) {
  await copyFile(join(source, file), join(destination, file));
}
console.log(`Build ready: ${destination} (${requiredFiles.length} files)`);
