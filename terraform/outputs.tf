output "ecs_service_name" { value = aws_ecs_service.fastapi_service.name }
output "db_endpoint" { value = aws_db_instance.postgres.address }
output "ecr_url" { value = aws_ecr_repository.fastapi.repository_url }