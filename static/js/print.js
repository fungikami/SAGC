function printData() {
   var head = document.getElementsByTagName('head')[0];
   var divToPrint=document.getElementById("tabla_cosechas");
   var titulo = document.getElementById("Nombre-Cosecha");
   newWin= window.open("Imprimir_cosechas.html");
   newWin.document.write(head.innerHTML);
   // Write title to the table
   newWin.document.write('<h1>Recolección de Cosechas de Cacao</h1>');
   console.log(titulo)
   newWin.document.write("<h2>" + titulo.innerHTML + "</h2>");

   newWin.document.write(divToPrint.outerHTML);
   // Delete the last column
   var tble = newWin.document.getElementById('tabla_cosechas');
   var row = tble.rows;
   var i = 11
   
   // If the table has more than 11 columns delete the last one
    if (tble.rows[0].cells.length > 11) {
        for (var j = 0; j < row.length; j++) {
            row[j].deleteCell(i);   
        }
    }
   newWin.print();
   // newWin.close();
}

const print = document.getElementById('printer');
var titulo = document.getElementById("Nombre-Cosecha");
console.log(titulo)
print.addEventListener('click', printData);