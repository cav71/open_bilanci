/**
 * Created by stefano on 2/6/14.
 */

function (doc) {
var considered_keys= [ "consuntivo", "preventivo" ];
var considered_quadro=['01','02','03','04','05','08','09','10','11','12','50'];
var tipo_bilancio = considered_keys[0];
    if(doc!==null){
              if(tipo_bilancio in doc){
                if(doc[tipo_bilancio]!==null){

                for (var j = 0; j < considered_quadro.length; j++) {
                          quadro_n = considered_quadro[j];
                          if( quadro_n in doc[tipo_bilancio] ){
                            for( var nome_titolo in doc[tipo_bilancio][quadro_n]){

                     if('data' in doc[tipo_bilancio][quadro_n][nome_titolo]){
                         for(funzione in doc[tipo_bilancio][quadro_n][nome_titolo]['data']){
                            if(funzione.indexOf("- ") == 0){
                             funzione = funzione.replace("- ","");
                             }
                             if(funzione!=''){
                                emit([tipo_bilancio+"_"+quadro_n+"_"+nome_titolo,funzione.toLowerCase()]);
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
