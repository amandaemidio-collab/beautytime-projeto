// Add STATUS_CPF record
query status_cpf verb=POST {
  api_group = "aula unicidade"

  input {
    dblink {
      table = "STATUS_CPF"
    }
  }

  stack {
    db.add STATUS_CPF {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $status_cpf
  }

  response = $status_cpf
  guid = "QLL_fKxjDq7gMQUkNZgIIC1OuZo"
}