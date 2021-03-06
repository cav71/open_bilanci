
function (doc) {
	var considered_keys= [ 'consuntivo', 'preventivo' ];
	var considered_quadro=['04','05','08','09','10','11','12'];
    var tipo_bilancio = considered_keys[0];
    if(doc!==null){
        if(tipo_bilancio in doc){
            if(doc[tipo_bilancio]!==null){

                for (var j = 0; j < considered_quadro.length; j++) {
                    quadro_n = considered_quadro[j];
                    if( quadro_n in doc[tipo_bilancio] ){
                        // fino al 2007 gli interventi stanno nel sottotitolo delle tabelle
                        for( var nome_titolo in doc[tipo_bilancio][quadro_n]){
                            if('meta' in doc[tipo_bilancio][quadro_n][nome_titolo]){
                                if('columns' in doc[tipo_bilancio][quadro_n][nome_titolo]['meta']){

                                    for(var k=0; k < doc[tipo_bilancio][quadro_n][nome_titolo]['meta']['columns'].length; k++){
                                        var intervento_b = doc[tipo_bilancio][quadro_n][nome_titolo]['meta']['columns'][k];
                                        emit([quadro_n+nome_titolo, intervento_b.toLowerCase()])
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
 }