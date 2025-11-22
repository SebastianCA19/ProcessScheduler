import azure.functions as func
import logging
import os
import sys

# Ajustar el path para importar módulos desde la raíz
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from scheduler_script import run_postulacion_checker

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function HTTP Trigger para ejecutar el scheduler de notificaciones.
    Esta función puede ser invocada desde Azure Data Factory o manualmente.
    """
    logging.info('ProcessScheduler function received a request.')
    
    # Validación opcional de seguridad
    # auth_header = req.headers.get('Authorization')
    # if not auth_header or auth_header != f"Bearer {os.environ.get('SCHEDULER_SECRET')}":
    #     return func.HttpResponse("Unauthorized", status_code=401)
    
    try:
        # Ejecutar la lógica principal
        logging.info("Iniciando ejecución del scheduler...")
        run_postulacion_checker()
        logging.info("Scheduler ejecutado correctamente.")
        
        return func.HttpResponse(
            "Scheduler executed successfully.",
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        error_msg = f"Error crítico durante la ejecución del scheduler: {str(e)}"
        logging.error(error_msg, exc_info=True)
        
        return func.HttpResponse(
            error_msg,
            status_code=500,
            mimetype="application/json"
        )