from flask_security import auth_required, roles_accepted
from flask_restful import Resource, reqparse
from flask import send_file
from tasks import generate_admin_report
import os
from celery.result import AsyncResult

# Simple CSV Export Parser
csv_export_start = reqparse.RequestParser()
csv_export_start.add_argument('period', type=str, required=False, location='json')

csv_export_status = reqparse.RequestParser()
csv_export_status.add_argument('task_id', type=str, required=True, location='json')

class UserAttemptsCSVExport(Resource):
    @auth_required('token')
    @roles_accepted('admin')
    def post(self):
        args = csv_export_start.parse_args()
        period = args.get('period')
        
        if period not in ['last_30_days', 'all_time']:
            return {"code": 400, "error_message": "Invalid period. Use 'last_30_days' or 'all_time'"}, 400
        
        
        try:
            # Start async CSV generation task
            task = generate_admin_report.delay(period)

            return {
                "code": 200,
                "message": "CSV export initiated successfully",
                "task_id": task.id,
                "status": "processing"
            }, 200
            
        except Exception as error:
            return {"code": 500, "error_message": f"Failed to initiate export: {str(error)}"}, 500


class CSVExportStatus(Resource):
    @auth_required('token')
    @roles_accepted('admin')
    def post(self):
        args = csv_export_status.parse_args()
        task_id = args.get('task_id')
        
        try:
            task_result = AsyncResult(task_id)
            
            if task_result.ready():
                if task_result.successful():
                    
                    # Task completed successfully
                    status = task_result.result.get("status")
                    
                    
                    return {
                        "code": 200,
                        "status": status,
                        "message": "Export completed successfully"
                    }, 200
                else:
                    # Task failed
                    error_message = str(task_result.result) if task_result.result else "Unknown error"
                    return {
                        "code": 500,
                        "status": "failed",
                        "error_message": error_message
                    }, 500
            else:
                # Task is still processing
                return {
                    "code": 200,
                    "status": "processing",
                    "message": "Export is still being processed"
                }, 200
                
        except Exception as error:
            return {"code": 500, "error_message": f"Error checking export status: {str(error)}"}, 500


class CSVExportDownload(Resource):
    def get(self, task_id):
        
        file_path = AsyncResult(task_id).result.get("file_path")

        try:
            
            if not os.path.exists(file_path):
                return {"code": 404, "error_message": "Export file not found or expired"}, 404
            
            return send_file(
                file_path,
                as_attachment=True,
                download_name=os.path.basename(file_path),
                mimetype='text/csv'
            )
            
        except Exception as error:
            return {"code": 500, "error_message": f"Error downloading file: {str(error)}"}, 500
    