
       function (doc) {
        var considered_keys= [ "consuntivo", "preventivo" ];
        var considered_quadro=['01','02','03','04','05','06'];
        var tipo_bilancio = considered_keys[1];
            if(doc!==null){
                	  if(tipo_bilancio in doc){
                	  	if(doc[tipo_bilancio]!==null){

                        for (var j = 0; j < considered_quadro.length; j++) {
                          quadro_n = considered_quadro[j];
                          if( quadro_n in doc[tipo_bilancio] ){
                            for( var nome_titolo in doc[tipo_bilancio][quadro_n]){
                             emit([tipo_bilancio+"_"+quadro_n+"_"+nome_titolo],1);
                            }
                          }
                        }
                    }
                	}

           }
        }