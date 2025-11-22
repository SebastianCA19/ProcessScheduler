import os
import logging
from sqlmodel import create_engine, Session
from typing import Generator

# Configuración básica del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- AJUSTA ESTAS IMPORTACIONES SEGÚN LA UBICACIÓN DE TUS ARCHIVOS ---
# Asume que el handler de Azure Function ajusta el sys.path para encontrar src/
from src.services.postulacion_notificacion_service import PostulacionNotificacionService
from src.repositories.notificacion_repo import NotificacionRepository
from src.repositories.convocatoria_snapshot_repo import ConvocatoriaSnapshotRepository
from src.repositories.analytic_repo import NotificacionAnalyticsRepository
# ----------------------------------------------------------------------

# 1. Configuración de la base de datos (Lee la cadena de conexión de Azure Settings)
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    logger.error("La variable de entorno DATABASE_URL no está configurada.")
    # En un entorno de producción, esto debería levantar una excepción
    raise EnvironmentError("Falta la configuración de DATABASE_URL.")

# Crea el motor de SQLAlchemy
engine = create_engine(DATABASE_URL)

def get_db_session() -> Generator[Session, None, None]:
    """Generador que proporciona una sesión de base de datos."""
    # El Session(engine) actúa como context manager para asegurar el cierre.
    with Session(engine) as session:
        yield session

def run_postulacion_checker():
    """Ejecuta la lógica de verificación y creación de notificaciones."""
    logger.info("Iniciando verificación programada de postulaciones...")
    
    # 2. Obtiene la sesión principal para la ejecución de la tarea
    session_generator = get_db_session()
    
    try:
        session = next(session_generator)
        
        # 3. Inicializa los repositorios
        # NOTA: NotificacionRepository NO recibe la sesión aquí, ya que su método create_
        # gestiona su propia sesión para transacciones aisladas.
        notificacion_repo = NotificacionRepository(session=session)
        snapshot_repo = ConvocatoriaSnapshotRepository(session=session)
        analytics_repo = NotificacionAnalyticsRepository(session=session)

        service = PostulacionNotificacionService(
            notificacion_repo=notificacion_repo,
            snapshot_repo=snapshot_repo,
            analytics_repo=analytics_repo
        )
        
        # 4. Ejecuta el proceso de negocio.
        # La sesión 'session' solo se usa aquí para los repositorios inyectados 
        # (snapshot y analytics).
        resultado = service.procesar_nuevas_postulaciones(session)
        
        logger.info(f"Tarea completada. Resultado: {resultado}")
        
    except StopIteration:
        logger.error("Error al iniciar la sesión de base de datos.")
    except Exception as e:
        logger.error(f"Error crítico en el checker: {e}")
        # Re-lanza la excepción para que el handler de Azure Function capture el error 500
        raise e
    finally:
        # Asegura el cierre correcto del generador
        try:
            next(session_generator)
        except StopIteration:
            pass

# NOTA: Se elimina el bloque if __name__ == "__main__": 
# para que el script no se ejecute automáticamente al ser importado por la Azure Function,
# sino solo cuando se llama explícitamente a run_postulacion_checker().