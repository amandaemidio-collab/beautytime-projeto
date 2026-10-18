// Get STATUS_CPF record
query "status_cpf/{status_cpf_id}" verb=GET {
  api_group = "aula unicidade"

  input {
    int status_cpf_id? filters=min:1
  }

  stack {
    db.get STATUS_CPF {
      field_name = "id"
      field_value = $input.status_cpf_id
    } as $status_cpf
  
    precondition ($status_cpf != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $status_cpf
  guid = "bThvBUbIKgIGVFcYJ4Ly--XZGbw"
}