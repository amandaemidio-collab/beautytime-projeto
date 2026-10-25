// Validates that every selected service is active and belongs to the company.
function "Catalogo/validate_professional_services" {
  input {
    int account_id
    int[] service_ids
  }

  stack {
    precondition (($input.service_ids|count) > 0) {
      error_type = "inputerror"
      error = "professional_requires_service"
    }

    precondition (($input.service_ids|count) == ($input.service_ids|unique|count)) {
      error_type = "inputerror"
      error = "professional_service_duplicate"
    }

    foreach ($input.service_ids) {
      each as $service_id {
        db.get service {
          field_name = "id"
          field_value = $service_id
          output = ["id", "account_id", "is_active"]
        } as $service

        precondition ($service != null && $service.account_id == $input.account_id && $service.is_active == true) {
          error_type = "inputerror"
          error = "professional_service_invalid"
        }
      }
    }
  }

  response = $input.service_ids
  guid = "Lu3xWukcHhmPafrSfQSXo35N0do"
}
