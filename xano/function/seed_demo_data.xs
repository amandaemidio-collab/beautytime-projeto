function "seed_demo_data" {
  description = "Create missing BeautyTime demo accounts, users, catalogs, hours and appointments without modifying existing records."

  input {
    password demo_password
  }

  stack {
    var $salon_specs {
      value = [
        {
          name: "Salão Aurora - Pinheiros"
          public_identifier: "salao-aurora"
          description: "Salão de beleza com serviços de cabelo e manicure."
          location: "Pinheiros, São Paulo - SP"
          owner_name: "Mariana Oliveira"
          owner_email: "dono.salao-aurora@demo.beautytime"
          professionals: ["Ana Lima", "Bruna Costa"]
          services: [
            {name: "Corte feminino", name_key: "corte feminino", duration_minutes: 60, price_cents: 12000}
            {name: "Escova", name_key: "escova", duration_minutes: 45, price_cents: 8000}
            {name: "Coloração de raiz", name_key: "coloração de raiz", duration_minutes: 120, price_cents: 22000}
            {name: "Hidratação capilar", name_key: "hidratação capilar", duration_minutes: 60, price_cents: 14000}
            {name: "Manicure clássica", name_key: "manicure clássica", duration_minutes: 60, price_cents: 6500}
          ]
        }
        {
          name: "Barbearia Paulista"
          public_identifier: "barbearia-paulista"
          description: "Barbearia com cortes, barba e cuidados masculinos."
          location: "Bela Vista, São Paulo - SP"
          owner_name: "Rafael Martins"
          owner_email: "dono.barbearia-paulista@demo.beautytime"
          professionals: ["Lucas Martins", "Pedro Souza"]
          services: [
            {name: "Corte clássico", name_key: "corte clássico", duration_minutes: 45, price_cents: 6000}
            {name: "Corte degradê", name_key: "corte degradê", duration_minutes: 60, price_cents: 7500}
            {name: "Barba completa", name_key: "barba completa", duration_minutes: 45, price_cents: 5500}
            {name: "Corte e barba", name_key: "corte e barba", duration_minutes: 90, price_cents: 10500}
            {name: "Pigmentação de barba", name_key: "pigmentação de barba", duration_minutes: 30, price_cents: 4000}
          ]
        }
        {
          name: "Estúdio Unhas Bela"
          public_identifier: "estudio-unhas-bela"
          description: "Estúdio especializado em manicure, pedicure e alongamento."
          location: "Vila Mariana, São Paulo - SP"
          owner_name: "Camila Ferreira"
          owner_email: "dono.estudio-unhas-bela@demo.beautytime"
          professionals: ["Camila Rocha", "Júlia Santos"]
          services: [
            {name: "Manicure clássica", name_key: "manicure clássica", duration_minutes: 60, price_cents: 6000}
            {name: "Pedicure", name_key: "pedicure", duration_minutes: 60, price_cents: 7000}
            {name: "Esmaltação em gel", name_key: "esmaltação em gel", duration_minutes: 75, price_cents: 11000}
            {name: "Alongamento em gel", name_key: "alongamento em gel", duration_minutes: 120, price_cents: 18000}
            {name: "Manutenção de alongamento", name_key: "manutenção de alongamento", duration_minutes: 90, price_cents: 14000}
          ]
        }
      ]
    }

    var $client_specs {
      value = [
        {name: "Cliente Demonstração 1", email: "cliente1@demo.beautytime"}
        {name: "Cliente Demonstração 2", email: "cliente2@demo.beautytime"}
        {name: "Cliente Demonstração 3", email: "cliente3@demo.beautytime"}
        {name: "Cliente Demonstração 4", email: "cliente4@demo.beautytime"}
      ]
    }

    precondition (($input.demo_password|strlen) >= 8) {
      error_type = "inputerror"
      error = "A senha de demonstração deve ter pelo menos 8 caracteres."
    }

    var $missing_salons {
      value = []
    }

    foreach ($salon_specs) {
      each as $salon_spec {
        db.get account {
          field_name = "public_identifier"
          field_value = $salon_spec.public_identifier
          output = ["id"]
        } as $existing_account

        conditional {
          if ($existing_account == null) {
            db.get user {
              field_name = "email"
              field_value = $salon_spec.owner_email
              output = ["id"]
            } as $existing_owner

            precondition ($existing_owner == null) {
              error_type = "inputerror"
              error = "Um e-mail reservado para dono demo já está em uso."
            }

            array.push $missing_salons {
              value = $salon_spec
            }
          }
        }
      }
    }

    foreach ($client_specs) {
      each as $client_spec {
        db.get user {
          field_name = "email"
          field_value = $client_spec.email
          output = ["id", "role", "account_id"]
        } as $existing_client

        conditional {
          if ($existing_client != null) {
            precondition ($existing_client.role == "client" && $existing_client.account_id == null) {
              error_type = "inputerror"
              error = "Um e-mail reservado para cliente demo pertence a uma conta incompatível."
            }
          }
        }
      }
    }

    var $today_start {
      value = (now|format_timestamp:"Y-m-d":"America/Sao_Paulo")|to_timestamp:"America/Sao_Paulo"
    }

    var $weekday {
      value = (now|format_timestamp:"N":"America/Sao_Paulo")|to_int
    }

    var $week_start {
      value = $today_start - (($weekday - 1) * 86400000)
    }

    var $future_start_1 {
      value = $today_start + 61200000
    }

    var $future_start_2 {
      value = $today_start + 61200000
    }

    var $future_start_3 {
      value = $today_start + 64800000
    }

    var $past_candidates {
      value = [
        {day_offset: 0, minute: 540}
        {day_offset: 0, minute: 720}
        {day_offset: 1, minute: 540}
        {day_offset: 1, minute: 720}
        {day_offset: 2, minute: 540}
        {day_offset: 2, minute: 720}
        {day_offset: 3, minute: 540}
        {day_offset: 3, minute: 720}
        {day_offset: 4, minute: 540}
        {day_offset: 4, minute: 720}
        {day_offset: 5, minute: 540}
        {day_offset: 5, minute: 720}
      ]
    }

    var $past_slots {
      value = []
    }

    foreach ($past_candidates) {
      each as $candidate {
        var $candidate_start {
          value = $week_start + ($candidate.day_offset * 86400000) + ($candidate.minute * 60000)
        }

        conditional {
          if ($candidate_start < now && ($past_slots|count) < 7) {
            var $slot_number {
              value = $past_slots|count
            }

            var $slot_status {
              value = "agendado"
            }

            conditional {
              if ($slot_number == 2 || $slot_number == 6) {
                var.update $slot_status {
                  value = "cancelado"
                }
              }
            }

            array.push $past_slots {
              value = {
                starts_at: $candidate_start
                slot_number: $slot_number
                status: $slot_status
              }
            }
          }
        }
      }
    }

    conditional {
      if (($missing_salons|count) > 0) {
        precondition ($weekday >= 1 && $weekday <= 6 && now <= ($future_start_1 - 3600000)) {
          error_type = "inputerror"
          error = "Os três horários demo de hoje precisam continuar no futuro e respeitar a antecedência mínima de uma hora."
        }

        precondition (($past_slots|count) == 7) {
          error_type = "inputerror"
          error = "Não há sete horários passados disponíveis na semana corrente."
        }
      }
    }

    db.transaction {
      stack {
        var $client_ids {
          value = []
        }

        var $clients_created {
          value = 0
        }

        foreach ($client_specs) {
          each as $client_spec {
            db.get user {
              field_name = "email"
              field_value = $client_spec.email
              output = ["id", "role", "account_id"]
            } as $existing_client

            conditional {
              if ($existing_client == null) {
                db.add user {
                  enforce_hidden_fields = false
                  data = {
                    name: $client_spec.name
                    email: $client_spec.email
                    password: $input.demo_password
                    account_id: null
                    role: "client"
                  }
                } as $created_client

                array.push $client_ids {
                  value = $created_client.id
                }

                var.update $clients_created {
                  value = $clients_created + 1
                }
              }

              else {
                precondition ($existing_client.role == "client" && $existing_client.account_id == null) {
                  error_type = "inputerror"
                  error = "Um e-mail reservado para cliente demo pertence a uma conta incompatível."
                }

                array.push $client_ids {
                  value = $existing_client.id
                }
              }
            }
          }
        }

        var $salon_results {
          value = []
        }

        foreach ($salon_specs) {
          each as $salon_spec {
            db.get account {
              field_name = "public_identifier"
              field_value = $salon_spec.public_identifier
              output = ["id"]
            } as $existing_account

            conditional {
              if ($existing_account == null) {
                db.get user {
                  field_name = "email"
                  field_value = $salon_spec.owner_email
                  output = ["id"]
                } as $existing_owner

                precondition ($existing_owner == null) {
                  error_type = "inputerror"
                  error = "Um e-mail reservado para dono demo já está em uso."
                }

                db.add account {
                  data = {
                    name: $salon_spec.name
                    public_identifier: $salon_spec.public_identifier
                    description: $salon_spec.description
                    location: $salon_spec.location
                  }
                } as $created_account

                db.add user {
                  enforce_hidden_fields = false
                  data = {
                    name: $salon_spec.owner_name
                    email: $salon_spec.owner_email
                    password: $input.demo_password
                    account_id: $created_account.id
                    role: "admin"
                  }
                } as $created_owner

                var $created_services {
                  value = []
                }

                foreach ($salon_spec.services) {
                  each as $service_spec {
                    db.add service {
                      data = {
                        account_id: $created_account.id
                        name: $service_spec.name
                        name_key: $service_spec.name_key
                        duration_minutes: $service_spec.duration_minutes
                        price_cents: $service_spec.price_cents
                        is_active: true
                      }
                    } as $created_service

                    array.push $created_services {
                      value = $created_service
                    }
                  }
                }

                var $created_professionals {
                  value = []
                }

                foreach ($salon_spec.professionals) {
                  each as $professional_name {
                    db.add professional {
                      data = {
                        account_id: $created_account.id
                        name: $professional_name
                        is_active: true
                      }
                    } as $created_professional

                    array.push $created_professionals {
                      value = $created_professional
                    }
                  }
                }

                foreach ($created_professionals) {
                  each as $created_professional {
                    foreach ($created_services) {
                      each as $created_service {
                        db.add professional_service {
                          data = {
                            professional_id: $created_professional.id
                            service_id: $created_service.id
                          }
                        } as $professional_service
                      }
                    }

                    foreach (1..6) {
                      each as $day_of_week {
                        db.add professional_hours {
                          data = {
                            professional_id: $created_professional.id
                            day_of_week: $day_of_week
                            start_minute: 540
                            end_minute: 1140
                          }
                        } as $professional_hour
                      }
                    }
                  }
                }

                foreach ($past_slots) {
                  each as $slot {
                    var $service_index {
                      value = $slot.slot_number % 5
                    }

                    var $professional_index {
                      value = $slot.slot_number % 2
                    }

                    var $client_index {
                      value = $slot.slot_number % 4
                    }

                    var $selected_service {
                      value = $created_services[$service_index]
                    }

                    var $selected_professional {
                      value = $created_professionals[$professional_index]
                    }

                    db.add appointment {
                      data = {
                        account_id: $created_account.id
                        client_id: $client_ids[$client_index]
                        professional_id: $selected_professional.id
                        service_id: $selected_service.id
                        starts_at: $slot.starts_at
                        ends_at: $slot.starts_at + ($selected_service.duration_minutes * 60000)
                        status: $slot.status
                        is_late_cancellation: false
                        service_name: $selected_service.name
                        service_duration_minutes: $selected_service.duration_minutes
                        service_price_cents: $selected_service.price_cents
                      }
                    } as $created_appointment
                  }
                }

                var $future_service {
                  value = $created_services[1]
                }

                var $future_professional_1 {
                  value = $created_professionals[0]
                }

                var $future_professional_2 {
                  value = $created_professionals[1]
                }

                db.add appointment {
                  data = {
                    account_id: $created_account.id
                    client_id: $client_ids[0]
                    professional_id: $future_professional_1.id
                    service_id: $future_service.id
                    starts_at: $future_start_1
                    ends_at: $future_start_1 + ($future_service.duration_minutes * 60000)
                    status: "agendado"
                    is_late_cancellation: false
                    service_name: $future_service.name
                    service_duration_minutes: $future_service.duration_minutes
                    service_price_cents: $future_service.price_cents
                  }
                } as $created_future_appointment

                db.add appointment {
                  data = {
                    account_id: $created_account.id
                    client_id: $client_ids[1]
                    professional_id: $future_professional_2.id
                    service_id: $future_service.id
                    starts_at: $future_start_2
                    ends_at: $future_start_2 + ($future_service.duration_minutes * 60000)
                    status: "agendado"
                    is_late_cancellation: false
                    service_name: $future_service.name
                    service_duration_minutes: $future_service.duration_minutes
                    service_price_cents: $future_service.price_cents
                  }
                } as $created_future_appointment_2

                db.add appointment {
                  data = {
                    account_id: $created_account.id
                    client_id: $client_ids[2]
                    professional_id: $future_professional_1.id
                    service_id: $future_service.id
                    starts_at: $future_start_3
                    ends_at: $future_start_3 + ($future_service.duration_minutes * 60000)
                    status: "agendado"
                    is_late_cancellation: false
                    service_name: $future_service.name
                    service_duration_minutes: $future_service.duration_minutes
                    service_price_cents: $future_service.price_cents
                  }
                } as $created_future_appointment_3

                db.query appointment {
                  where = $db.appointment.account_id == $created_account.id && $db.appointment.starts_at >= $week_start && $db.appointment.starts_at < ($week_start + 604800000)
                  return = {type: "count"}
                } as $appointments_created_count

                db.query appointment {
                  where = $db.appointment.account_id == $created_account.id && $db.appointment.starts_at >= $today_start && $db.appointment.starts_at < ($today_start + 86400000)
                  return = {type: "count"}
                } as $appointments_today_count

                db.query appointment {
                  where = $db.appointment.account_id == $created_account.id && $db.appointment.starts_at >= $week_start && $db.appointment.starts_at < ($week_start + 604800000) && $db.appointment.status == "cancelado"
                  return = {type: "count"}
                } as $cancelled_appointments_count

                array.push $salon_results {
                  value = {
                    name: $salon_spec.name
                    public_identifier: $salon_spec.public_identifier
                    owner_email: $salon_spec.owner_email
                    appointments_created: $appointments_created_count
                    appointments_today: $appointments_today_count
                    cancelled_appointments: $cancelled_appointments_count
                  }
                }
              }

              else {
                array.push $salon_results {
                  value = {
                    name: $salon_spec.name
                    public_identifier: $salon_spec.public_identifier
                    owner_email: $salon_spec.owner_email
                    appointments_created: 0
                    appointments_today: 0
                    cancelled_appointments: 0
                  }
                }
              }
            }
          }
        }
      }
    }
  }

  response = {
    clients_created: $clients_created
    salons: $salon_results
  }
  guid = "jQ_aaDkm0xn09C4Ht--Xpw1i0kU"
}
