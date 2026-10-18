// Delete teste aula record.
query "teste_aula/{teste_aula_id}" verb=DELETE {
  api_group = "Event Logs"

  input {
    int teste_aula_id? filters=min:1
  }

  stack {
    db.del "teste aula" {
      field_name = "id"
      field_value = $input.teste_aula_id
    }
  }

  response = null
  guid = "yMoUwF1DX8VWGdV2-giIrXjZuz8"
}