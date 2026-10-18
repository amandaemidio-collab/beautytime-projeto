// Query all STATUS_CPF records
query status_cpf verb=GET {
  api_group = "aula unicidade"

  input {
  }

  stack {
    db.query STATUS_CPF {
      return = {type: "list"}
    } as $status_cpf
  }

  response = $status_cpf
  guid = "cm3q_7u-VX1hHTQhr0T6jbsMWFw"
}