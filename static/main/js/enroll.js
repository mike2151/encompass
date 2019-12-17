$(function(){
  $("#payment_form").hide();
  $("#plan_1").addClass("active");

  $("#success_div").css("display","none");
  $("#error_div").css("display","none");
  $("#payment_loading").css("display","none");
});

$("#plan_0").hover(
  function() {
    $(this).addClass("active");
    $("#plan_1").removeClass("active");
    $("#plan_2").removeClass("active");
  }
);

$("#plan_1").hover(
  function() {
    $(this).addClass("active");
    $("#plan_0").removeClass("active");
    $("#plan_2").removeClass("active");
  }
);

$("#plan_2").hover(
  function() {
    $(this).addClass("active");
    $("#plan_0").removeClass("active");
    $("#plan_1").removeClass("active");
  }
);

var stripe_key = location.protocol != 'https:' ? 'pk_test_ioV3Z9uubVlAzLlAPgN5lX8v00LFLd0e5v' : 'pk_live_ct6Q6viO6x3NrruDeTnCrr6b00XeFjzqbG'
var stripe = Stripe(stripe_key);
var elements = stripe.elements();

var style = {
  base: {
    fontSize: '16px',
    color: "#32325d",
  }
};

var card = elements.create('card', {style: style});
card.mount('#example-card');

function showPayment(event) {
  var referring_element = event;
  var num_questions = referring_element.getAttribute("num_questions");
  $("#payment_form").show();
  $("#payment_form").attr("num_questions", num_questions);
  $("#card_title").html("Pay With Card: " + num_questions.toString() + " Question Creator");
}

function turnOffAutoRenew() {
  var CSRFtoken=$('input[name=csrfmiddlewaretoken]').val();
  fetch('/users/cancel_auto_renewal/', {
    method: 'post',
    headers: {
      'Content-Type': 'application/json',
      "X-CSRFToken": CSRFtoken
    },
    body: JSON.stringify({
      csrfmiddlewaretoken: CSRFtoken
    })
  }).then(response => {
    location.reload();
  }); 
}

function turnOnAutoRenew() {
  var CSRFtoken=$('input[name=csrfmiddlewaretoken]').val();
  fetch('/users/activate_auto_renewal/', {
    method: 'post',
    headers: {
      'Content-Type': 'application/json',
      "X-CSRFToken": CSRFtoken
    },
    body: JSON.stringify({
      csrfmiddlewaretoken: CSRFtoken
    })
  }).then(response => {
    location.reload();
  }); 
}

function submitPayment () {
  $("#error_div").css("display","none");
  $("#success_div").css("display","none");
  $("#payment_loading").css("display","block");
  $("#error_message").html("");
  stripe.createPaymentMethod({
    type: 'card',
    card: card,
    billing_details: {},
  }).then(function(result) {
    if (result.error) {
      $("#error_div").css("display","block");
      document.getElementById("error_message").innerHTML = result.error["message"];
      $("#payment_loading").css("display","none");
    } else {
      var CSRFtoken=$('input[name=csrfmiddlewaretoken]').val();
      var num_questions = document.getElementById("payment_form").getAttribute("num_questions")
      fetch('/users/enroll_in_membership/', {
        method: 'post',
        headers: {
          'Content-Type': 'application/json',
          "X-CSRFToken": CSRFtoken
        },
        body: JSON.stringify({
          payment_method: result.paymentMethod["id"],
          num_questions: num_questions,
          csrfmiddlewaretoken: CSRFtoken
        })
      }).then(response => {
        return response.json();
      }).then(data => {
        var success = data["success"];
        $("#payment_loading").css("display","none");
        if (success) {
          $("#success_div").css("display","block");
          document.getElementById("success_message").innerHTML = data["message"];
        } else {
          $("#error_div").css("display","block");
          document.getElementById("error_message").innerHTML = data["message"];
        }
      });
    }
  });
}

