catalogApp.controller('profileCtrl', ['$scope','$auth','$modal','$http','userService', 'itemService', 'categoryService',
	function($scope,$auth,$modal,$http, userService, itemService, categoryService){


		categoryService.getAllCategories().then(function(data){
			$scope.categories = data.categories;
		}, function(err) {
			console.log(err)
		});

		$scope.getCategoryName = function(id) {
		  for (var i = 0; i < $scope.categories.length; i++) {
		    if ($scope.categories[i]['id'] === id) {
		      return $scope.categories[i]['name'];
		    }
		  }
		  return null;
		}

		// Pre-fetch an external template populated with a custom scope
		var myOtherModal = $modal({scope: $scope, templateUrl: '/static/client/components/profile/new_item_form.html', show: false});
		// Show when some event occurs (use $promise property to ensure the template has been loaded)
		$scope.showModal = function() {
		  myOtherModal.$promise.then(myOtherModal.show);
		};


		$scope.formData = {
			name: 'enter a name',
			price: 50,
			description: 'desc',
			image: 'url',
			owner_id: $auth.getPayload().sub,
			category_name: 'testcategory'
		};

		userService.getUser($auth.getPayload().sub).then(function(data){
			$scope.user = data.user;
			$scope.myListings = data.items;
		}, function(err) {
			console.log(err)
		});

		// itemService.getMyListings($auth.getPayload().sub).then(function(data){
		// 	$scope.myListings = data.items;
		// }, function(err) {
		// 	console.log(err)
		// });
		$scope.edit = function(id){
			// itemService.getItem(id).then(function(data){
				



			// }, function(err) {
			// 	console.log(err)
			// });
			itemService.updateItem(id,id).then(function(data){
				alert(data)			
			}, function(err) {
				console.log(err)
			});
		}

		$scope.delete = function(id){
			itemService.deleteItem(id).then(function(data){
				alert(data)			
			}, function(err) {
				console.log(err)
			});
		}

		$scope.processForm = function(){
			itemService.addListing($scope.formData);
			myOtherModal.$promise.then(myOtherModal.hide);
		}


	}])