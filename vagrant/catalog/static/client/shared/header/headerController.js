catalogApp.controller('headerCtrl', ['$scope','$location','categoryService', 
	function($scope, $location, categoryService){

		// categoryService.getAllCategories(function(data) {
		// 	$scope.categories = data;
		// });

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

	}])