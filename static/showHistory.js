$(document).ready(function(){
    $.ajax({
        url : '/getHistory',
  
        success: function(data){
          $(data).each(function(){
            var transactionId = $(this)[0];
            var productName = $(this)[5];
            var price = $(this)[6];
            var quantity = $(this)[3];
            var info = '<tr><td>'+ transactionId +'</td><td>'+ productName + '</td><td> $'+ price + '</td><td>'+ quantity+ '</td></tr>';
            $("#history").find("tbody").append(info)
          });
        },
        error: function(error){console.log('error : '+error.responseText);}
      });
});