function printData()
{
   var head = document.getElementsByTagName('head')[0];
   var divToPrint=document.getElementById("tabla_cosechas");
   newWin= window.open("Imprimir_cosechas.html");
   newWin.document.write(head.innerHTML);
   newWin.document.write(divToPrint.outerHTML);
   // Delete the last column
   var tble = newWin.document.getElementById('tabla_cosechas');
   var row = tble.rows;
   var i = 11
   for (var j = 0; j < row.length; j++) {
      row[j].deleteCell(i);   
   }
   newWin.print();
   newWin.close();
}

const print = document.getElementById('printer');
print.addEventListener('click', printData);