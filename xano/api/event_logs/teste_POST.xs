// Add Teste record
query teste verb=POST {
  api_group = "Event Logs"

  input {
    dblink {
      table = "Teste"
    }
  }

  stack {
    db.add Teste {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $teste
  }

  response = $teste
  guid = "TPMBFwSJssMCD3tp5bpVdfH_nec"
}