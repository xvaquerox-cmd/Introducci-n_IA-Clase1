// Llama al mini servidor local (server.js)
const SERVIDOR = 'http://localhost:4000';

const lineaConsultando = document.getElementById('consultando');
const lineaResultado   = document.getElementById('resultado');

function formatFecha(fechaBanxico) {
  if (!fechaBanxico) return '—';
  const [dd, mm, yyyy] = fechaBanxico.split('/');
  const d = new Date(`${yyyy}-${mm}-${dd}T12:00:00`);
  return d.toLocaleDateString('es-MX', { day: '2-digit', month: 'long', year: 'numeric' });
}

function formatHora(iso) {
  return new Date(iso).toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit', hour12: true });
}

async function consultar() {
  try {
    const res  = await fetch(`${SERVIDOR}/tipo-cambio`);
    const data = await res.json();

    lineaResultado.textContent =
      `API BANXICO\n` +
      `Fecha ${formatFecha(data.fecha)}\n` +
      `Hora ${formatHora(data.cached_at)}\n` +
      `API Serie SF43718 Tipo de Cambio FIX ${data.fix}\n` +
      `API Serie SF343410 Tipo de Cambio Cierre ${data.cierre}`;

  } catch (e) {
    lineaResultado.textContent = 'Error: ' + e.message;
  }
}

consultar();
