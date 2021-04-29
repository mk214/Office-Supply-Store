$(document).ready(function(){
    $("#error36").hide();
    $("#successful").hide();
    loadTable();

    //Ajax Call to load page with the cart inforamtion
    function loadTable(){
        var total = 0;
        $.ajax({
            url : '/getCart',
      
            success: function(data){
              $(data).each(function(){
                var productName = $(this)[4];
                var price = $(this)[5];
                var quantity = "<span id=\"quantity\">"+$(this)[2]+"</span>";
                var del = "<span><i class=\"fa fa-trash\"></i></span>";
                var itemId = $(this)[1];
                var increaseQuantity = "<span><i class=\"fa fa-plus ml-4\"></i></span>";
                var decreaseQuantity =  "<span><i class=\"fa fa-minus mr-4\"></i></span>";
                var info = '<tr><td id=\"name\" itemid=\"'+itemId+'\">' + productName + '</td><td> $'+ price + '</td><td>'+decreaseQuantity+quantity+increaseQuantity+'</td><td>'+ del +'</td></tr>';
                $("#cart").find("tbody").append(info)
                total += price*$(this)[2];
              });
              $("#total").html("Total : $"+total);
            },
            error: function(error){console.log('error : '+error.responseText);}
          });
    }
    

      //Delete cart item
      $("table").on("click", ".fa-trash", function(){
            var send = {itemId:$(this).closest("tr").find("#name").attr("itemid")};
            $(this).closest("tr").remove();
              
            $.ajax({ 
                type:"DELETE",
                url:"/removeFromCart",
                data: JSON.stringify(send),
                dataType: "json",
                contentType: 'application/json'
            });
            $("#error36").hide();
        });

        //update quantities, instead of quantity being zero it is removed from cart
        $("table").on("click", ".fa-minus", function(){
            var quantity = $(this).closest("tr").find("#quantity").text()
            if(quantity > 1){
                var send = {itemId:$(this).closest("tr").find("#name").attr("itemid")};
                $.ajax({
                    type:"POST",
                    data: JSON.stringify(send),
                    dataType: "json",
                    contentType: 'application/json',
                    url : '/decreaseQuantityInCart',
                    success: function(data){
                        $( "#cart" ).load( location.href + " #cart" );
                        loadTable();
                        $("#error36").hide();
                    },
                    error: function(error){console.log('error : '+error.responseText);}
                  });
            }
            else{
                var send = {itemId:$(this).closest("tr").find("#name").attr("itemid")};
                $(this).closest("tr").remove();
                
                $.ajax({ 
                    type:"DELETE",
                    url:"/removeFromCart",
                    data: JSON.stringify(send),
                    dataType: "json",
                    contentType: 'application/json',
                    success: function(data){
                        $( "#cart" ).load( location.href + " #cart" );
                        loadTable();
                    },
                    error: function(error){console.log('error : '+error.responseText);}
                });
            }
        });
        $("table").on("click", ".fa-plus", function(){
            var send = {itemId:$(this).closest("tr").find("#name").attr("itemid")};
            $.ajax({
                type:"POST",
                data: JSON.stringify(send),
                dataType: "json",
                contentType: 'application/json',
                url : '/increaseQuantityInCart',
                success: function(data){
                    if(data["error"] == "36"){$("#error36").show();}
                    $( "#cart" ).load( location.href + " #cart" );
                    loadTable();
                },
                error: function(error){console.log('error : '+error.responseText);}
              });
        });

        //Checkout, remove everything from cart and add it to purchase history
        $("#checkout").click(function(){
            $.ajax({ 
                type:"POST",
                url:"/checkout",
                dataType: "json",
                contentType: 'application/json',
                success: function(data){
                    $("#successful").show();
                    console.log(data);
                    $( "#cart" ).load( location.href + " #cart" );
                    loadTable();
                },
                error: function(error){console.log('error : '+error.responseText);}
            });
        });
});