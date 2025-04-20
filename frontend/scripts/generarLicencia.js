// scripts/generarLicencia.js
require('dotenv').config();
const { writeFileSync, mkdirSync } = require('fs');
const licenceKey = process.env.SYNCFUSION_LICENSE;
const path = require('path');

// Ruta absoluta al fichero a generar
const filePath = path.join(__dirname, '../src/environments/syncfusion-license.ts');
if (filePath) {
  console.log('✅ Fichero syncfusion-license.ts ya existente.');
  process.exit(1);
}

if (!licenceKey) {
  console.error('❌ La variable SYNCFUSION_LICENSE no está definida.');
  process.exit(1);
}

// Asegurarte de que la carpeta existe
const dir = path.dirname(filePath);
mkdirSync(dir, { recursive: true });

const content = `// Este fichero NO debe comitearse: contiene la clave de Syncfusion
export const syncfusionLicense = '${licenceKey.replace(/'/g, "\\'")}';
`;

writeFileSync('src/environments/syncfusion-license.ts', content);
console.log('✅ Fichero syncfusion-license.ts generado.');