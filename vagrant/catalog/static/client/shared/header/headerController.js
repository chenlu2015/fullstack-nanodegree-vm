catalogApp.controller('headerCtrl', ['$scope','$location','$auth','$route','categoryService', 
	function($scope, $location, $auth, $route, categoryService){

		// categoryService.getAllCategories(function(data) {
		// 	$scope.categories = data;
		// });
		$scope.isAuthenticated = $auth.isAuthenticated();
		$scope.userID = $auth.getPayload();

		$scope.selectedCategory = {name: "All"};
		$scope.select = function(cat){
			$scope.selectedCategory = cat;
			console.log($scope.selectedCategory);
		}

		categoryService.getAllCategories().then(function(data){
			$scope.categories = data;
		}, function(err) {
			console.log(err)
		});

		// .then(function(data){
		// 	$scope.categories = data;
		// 	console.log(data)
		// })
		$scope.go = function ( path ) {
		  console.log(path);
		  $location.path( path );
		};

		$scope.logout = function() {
		  $auth.logout();
		  $location.path('/');
		  $route.reload();
		  alert('you have successfully logged out!');
		};

	}])