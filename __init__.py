import azure.functions as func
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 

from scheduler_script import run_postulacion_checker 

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('HTTP trigger ProcessScheduler received a request from ADF.')
    
    # Aquí puedes añadir una verificación de cabecera si quieres seguridad extra
    
    try:
        # Llama a la lógica de negocio principal
        run_postulacion_checker()
        
        logging.info("El scheduler_script se ejecutó correctamente.")
        
        return func.HttpResponse(
             "Scheduler executed successfully.",
             status_code=200
        )
    except Exception as e:
        logging.error(f"Error crítico durante la ejecución del scheduler: {e}")
        # Retorna 500 para que ADF sepa que la actividad falló
        return func.HttpResponse(
             f"Error en el scheduler: {e}",
             status_code=500
        )