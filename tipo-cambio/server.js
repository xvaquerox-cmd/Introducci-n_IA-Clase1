// ============================================================

//   node server.js

// ============================================================

const http  = require('http');   // Para crear el servidor local
const https = require('https');  // Para llamar a Banxico (HTTPS)
const fs    = require('fs');     // Para leer los archivos HTML/CSS/JS
const path  = require('path');   // Para construir rutas de archivos

// ── CONFIGURACIÓN ─────────────────────────────────────────
const PUERTO        = 4000;
const BANXICO_TOKEN = '6f56d2412aa2a3f530dc89983d7155349245ad9491464b9411766d6c65e5ee3c';
const BANXICO_URL   = 'https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43718,SF343410/datos/oportuno';

// ── Función que llama a Banxico ────────────────────────────
// Devuelve una Promesa con los datos del tipo de cambio
function consultarBanxico() {
  return new Promise((resolver, rechazar) => {
    const opciones = {
      headers: {
        'Bmx-Token': BANXICO_TOKEN,
        'Accept':    'application/json',
      }
    };

    https.get(BANXICO_URL, opciones, (respuesta) => {
      let datos = '';

      // Banxico manda la respuesta en partes — las juntamos
      respuesta.on('data', parte => datos += parte);

      // Cuando termina de llegar todo, procesamos
      respuesta.on('end', () => {
        try {
          const json   = JSON.parse(datos);
          const series = json.bmx.series;

          const fix    = series.find(s => s.idSerie === 'SF43718');
          const cierre = series.find(s => s.idSerie === 'SF343410');

          resolver({
            fix:       fix?.datos?.[0]?.dato    || 'N/D',
            cierre:    cierre?.datos?.[0]?.dato  || 'N/D',
            fecha:     fix?.datos?.[0]?.fecha    || '',
            fuente:    'banxico',
            cached_at: new Date().toISOString(),
          });
        } catch (e) {
          rechazar(new Error('Error al procesar respuesta de Banxico'));
        }
      });

    }).on('error', rechazar);
  });
}

// ── Tipos de archivo para servir el HTML/CSS/JS ────────────
const TIPOS = {
  '.html': 'text/html',
  '.css':  'text/css',
  '.js':   'text/javascript',
};

// ── El servidor ────────────────────────────────────────────
const servidor = http.createServer(async (req, res) => {

  // Endpoint de tipo de cambio — el frontend lo llama aquí
  if (req.url === '/tipo-cambio') {
    try {
      const datos = await consultarBanxico();
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(datos));
    } catch (e) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: e.message }));
    }
    return;
  }

  // Todo lo demás: servir archivos estáticos (index.html, app.js, estilo.css)
  const archivo = req.url === '/' ? '/index.html' : req.url;
  const ruta    = path.join(__dirname, archivo);
  const ext     = path.extname(ruta);

  if (fs.existsSync(ruta)) {
    res.writeHead(200, { 'Content-Type': TIPOS[ext] || 'text/plain' });
    res.end(fs.readFileSync(ruta));
  } else {
    res.writeHead(404);
    res.end('No encontrado');
  }
});

// ── Arrancar ───────────────────────────────────────────────
servidor.listen(PUERTO, () => {
  console.log(`Servidor corriendo en http://localhost:${PUERTO}`);
});
