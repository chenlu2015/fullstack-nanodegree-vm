catalogApp.controller('authController', ['$scope', '$auth',
	function($scope, $auth){
	  $scope.authenticate = function(provider) {
		  $auth.authenticate(provider).then(function(response){
		  	console.log('success!!');
		    console.log(response);
		    console.log($auth.getPayload());
		    console.log($auth.isAuthenticated());
		    $auth.logout();
		    console.log($auth.isAuthenticated());
		  }, function (err){
		  	console.log(err);
		  })
	  };
	}]);


// function signInCallback(authResult){
// 	console.log('signinCallback');
// 	if (authResult['code']){
// 		$('#signinButton').attr('style', 'display:none;');
// 		$.ajax({
// 			type:'POST',
// 			//url: '/gconnect?state={{STATE}}',
// 			url:'/api/v1.0/gconnect',
// 			processData: false,
// 			contentType: 'application/octet-stream; charset=utf-8',
// 			data: authResult['code'],
// 			success: function(result){
// 				if (result){
// 					$('#result').html('Login Successful! </br>' + result) 
// 					setTimeout(function(){
// 						window.location.href="/";
// 					}, 4000);
// 				} else if (authResult['error']){
// 					console.log(authResult['error']);
// 				} else {
// 					console.log('no return');
// 				}
// 			}
// 		})
// 	}
// }