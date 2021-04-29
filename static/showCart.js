$(document).ready(function(){
    var total = 0;

    //Ajax Call to load page with the cart inforamtion
    $.ajax({
        url : '/getCart',
  
        success: function(data){
          $(data).each(function(){
            var productName = $(this)[4];
            var price = $(this)[5];
            var quantity = $(this)[2];
            var del = "<span><i class=\"fa fa-trash\"></i></span>";
            var itemId = $(this)[1];
            var increaseQuantity = "<span><i class=\"fa fa-plus ml-4\"></i></span>";
            var decreaseQuantity =  "<span><i class=\"fa fa-minus mr-4\"></i></span>";
            var info = '<tr><td id=\"name\" itemid=\"'+itemId+'\">' + productName + '</td><td> $'+ price + '</td><td>'+decreaseQuantity+quantity+increaseQuantity+'</td><td>'+ del +'</td></tr>';
            $("#cart").find("tbody").append(info)
            total += price;
          });
          $("#total").html("Total : $"+total);
        },
        error: function(error){console.log('error : '+error.responseText);}
      });

      //Delete cart item
      $("table").on("click", ".fa-trash", function(){
            var send = {itemId:$(this).closest("tr").find("#name").attr("itemid")};
            console.log(send);
            $(this).closest("tr").remove();
              
            $.ajax({ 
                type:"DELETE",
                url:"/removeFromCart",
                data: JSON.stringify(send),
                dataType: "json",
                contentType: 'application/json'
            });
            location.reload(); 
        });

        //update quantities
        $("table").on("click", ".fa-minus", function(){
            console.log('test');
        });
        $("table").on("click", ".fa-plus", function(){
            console.log('test');
        });

        //Checkout, remove everything from cart and add it to purchase history
});