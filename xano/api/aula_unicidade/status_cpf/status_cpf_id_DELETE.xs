// Delete STATUS_CPF record.
query "status_cpf/{status_cpf_id}" verb=DELETE {
  api_group = "aula unicidade"

  input {
    int status_cpf_id? filters=min:1
  }

  stack {
    db.del STATUS_CPF {
      field_name = "id"
      field_value = $input.status_cpf_id
    }
  }

  response = null
  guid = "ix17ktV_H34W6QNP5o5guV1taIo"
}