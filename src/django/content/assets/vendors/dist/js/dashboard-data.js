/*Dashboard Init*/
"use strict";

/*****Ready function start*****/

/*****Ready function end*****/

/*****Load function start*****/


$('#gardenName').text(land_name);
$('#lastTemp').text(temp_value);
$('#today_water').text(today_water);
$('#toggle_spout').prop("checked", spout_1_condition);
$('#today_humidity').text(today_humidity);


$(window).on("load",function(){
	window.setTimeout(function(){
		$.toast({
			heading: 'به پتوس خوش آمدید',
			text: 'به پنل مدیریت پتوس خوش آمدید',
			position: 'bottom-left',
			loaderBg:'#e3c94b',
			icon: '',
			hideAfter: 3500,
			stack: 6
		});
	}, 3000);
});
/*****Load function* end*****/

/*****E-Charts function start*****/
var echartsConfig = function() {
	lastwater_weekly();
	soilmoisture_momentary();
	temperature_weekly();
	gdds_weekly();


  	if( $('#humiditySensor').length > 0 ){
		var humiditySensor = echarts.init(document.getElementById('humiditySensor'));
		var option1 = {
			animation: true,
			tooltip: {
				trigger: 'axis',
				backgroundColor: 'rgba(33,33,33,1)',
				borderRadius:0,
				padding:10,
				axisPointer: {
					type: 'cross',
					label: {
						backgroundColor: 'rgba(33,33,33,1)'
					}
				},
				textStyle: {
					color: '#fff',
					fontStyle: 'normal',
					fontWeight: 'normal',
					fontFamily: "'Montserrat', sans-serif",
					fontSize: 12
				}
			},
			color: '#154f57',
			grid: {
				top: 35,
				left:47,
				bottom: 20
			},
			xAxis: {
				type: 'value',
				position: 'top',
				axisLine: {
					show:false
				},
				axisLabel: {
					textStyle: {
						color: '#878787'
					}
				},
				splitLine: {
					show:false
				},
			},
			yAxis: {
				splitNumber: 25,
				type: 'category',
				show:true,
				axisLine: {
					show:false
				},
				axisLabel: {
					textStyle: {
						color: '#878787'
					}
				},
				axisTick: {
					show: true
				},
				splitLine: {
					show:false
				},
				data: past_week_days
			},
			series: [{
				name: 'رطوبت هوا',
				type: 'bar',
				barGap: '-100%',
				label: {
					normal: {
						textStyle: {
							color: '#682d19'
						},
						position: 'left',
						show: false,
						formatter: '{b}'
					}
				},
				itemStyle: {
					normal: {
						color: new echarts.graphic.LinearGradient(
							0, 1, 0, 0, [{
								offset: 0,
								color: '#208a5d'
							}, {
								offset: 1,
								color: '#154f57'
							}]
						)
					}
				},
				data: week_avg_humidity
			}]
		}
		humiditySensor.setOption(option1);
		humiditySensor.resize();
	}
}
/*****E-Charts function end*****/

/*****Sparkline function start*****/
var sparklineLogin = function() {
	if( $('#sparkline_4').length > 0 ){
		$("#sparkline_4").sparkline([2,4,4,6,8,5,6,4,8,6,6,2 ], {
			type: 'line',
			width: '100%',
			height: '35',
			lineColor: '#ffffff',
			fillColor: '#fff',
			minSpotColor: '#fff',
			maxSpotColor: '#fff',
			spotColor: '#fff',
			highlightLineColor: '#fff',
			highlightSpotColor: '#fff'
		});
	}
}
/*****Sparkline function end*****/

/*****Resize function start*****/
var sparkResize,echartResize;
$(window).on("resize", function () {
	/*Sparkline Resize*/
	clearTimeout(sparkResize);
	sparkResize = setTimeout(sparklineLogin, 200);

	/*E-Chart Resize*/
	clearTimeout(echartResize);
	echartResize = setTimeout(echartsConfig, 200);
}).resize();



/*****Resize function end*****/

var soilMoistureChartXaxisFlag;

$('#soilmoistureavgs_monthly').click(function(){ soilmoisture_monthly();return 1; });
$('#soilmoistureavgs_weekly').click(function(){ soilmoisture_weekly();return 1; });
$('#soilmoisture_momentary').click(function(){ soilmoisture_momentary();return 1; });

$('#lastwater_monthly').click(function(){ lastwater_monthly();return 1; });
$('#lastwater_weekly').click(function(){ lastwater_weekly();return 1; });

$('#monthlytemperature').click(function(){ temperature_monthly(); return 1; });
$('#weeklytemperature').click(function(){ temperature_weekly(); return 1; });

$('#gdds_monthly').click(function(){ gdds_monthly(); return 1; });
$('#gdds_weekly').click(function(){ gdds_weekly(); return 1; });
//////////////
var soilmoisture_monthly = function()
{
		if( $('#soilmoisture').length > 0 ) {
			var soilmoisture = echarts.init(document.getElementById('soilmoisture'));
			soilMoistureChartXaxisFlag = "monthly";
			var option3 = {
				// timeline: {
				// 	data: ['1', '2', '3', '4', '5', '6', '7', '8'],
				// 	axisType: 'category',
				// 	show: true,
				// 	autoPlay: false,
				// 	playInterval: 1000,
				// },
				timeline:{
					show:false
				},
				options: [{
					tooltip: {
						trigger: 'axis',
						backgroundColor: 'rgba(33,33,33,1)',
						borderRadius: 0,
						padding: 10,
						textStyle: {
							color: '#fff',
							fontStyle: 'normal',
							fontWeight: 'normal',
							fontFamily: "IRANSans",
							fontSize: 12
						}
					},
					dataZoom: [{show: false,}],
					calculable: true,
					grid: {
						show: false
					},
					xAxis: [{
						'type': 'category',
						axisLabel: {
							interval: 3,
							showMaxLabel: true,
							textStyle: {
								color: '#878787',
								fontStyle: 'normal',
								fontWeight: 'normal',
								fontFamily: "IRANSans",
								fontSize: 12

							},
							rotate:90
						},
                        boundaryGap: true,
						axisLine: {
							show: true
						},
						splitLine: {
							show: false
						},
                        position:'bottom',
						'data': past_month_days
					}],
					yAxis: [{
						'type': 'value',

						axisLine: {
							show: true
						},
						axisLabel: {
							textStyle: {
								color: '#878787',
								fontStyle: 'normal',
								fontWeight: 'normal',
								fontFamily: "IRANSans",
								fontSize: 12
							}
						},
						splitLine: {
							show: false,
						},
					}],
					series:[{
						'name': 'رطوبت خاک',
						'type': 'line',
						'data': month_soil_moisture_avgs,
						itemStyle: {
							normal: {
								color: new echarts.graphic.LinearGradient(
									0, 1, 0, 0, [{
										offset: 0,
										color: '#208a5d'
									}, {
										offset: 1,
										color: '#154f57'
									}]
								),
								barBorderRadius: 4
							},
							emphasis: {
								color: new echarts.graphic.LinearGradient(
									0, 1, 0, 0, [{
										offset: 0,
										color: '#208a5d'
									}, {
										offset: 1,
										color: '#fff'
									}]
								),
								barBorderRadius: 4
							}
						},
						label: {
							normal: {
								show: true,
								position: 'top',
								formatter: '{c}',
								color: '#fff',
								fontStyle: 'normal',
								fontWeight: 'normal',
								fontFamily: "IRANSans",
								fontSize: 12
							}
						},
					}]
				}]
			};
			console.log(soilvalue);
			soilmoisture.setOption(option3);
			soilmoisture.resize();
		}
}
var soilmoisture_weekly = function () {
		if( $('#soilmoisture').length > 0 ){
		var soilmoisture = echarts.init(document.getElementById('soilmoisture'));
		soilMoistureChartXaxisFlag = "weekly";
		var option3 = {
			timeline: {
				data: ['1', '2', '3', '4', '5', '6', '7', '8'],
				axisType: 'category',
				show: true,
				autoPlay: false,
				playInterval: 1000,
                top:'87%',
			},
			options: [{
				tooltip: {
					trigger: 'axis',
					backgroundColor: 'rgba(33,33,33,1)',
					borderRadius:0,
					padding:10,
					textStyle: {
						color: '#fff',
						fontStyle: 'normal',
						fontWeight: 'normal',
						fontFamily: "IRANSans",
						fontSize: 12
					}
				},
				calculable: false,
				grid: {
					show:false
				},
				dataZoom: [{show: false,}],
				xAxis: [{
					'type': 'category',
					axisLabel: {
						interval: 0,
						textStyle: {
							color: '#878787',
							fontStyle: 'normal',
							fontWeight: 'normal',
							fontFamily: "IRANSans",
							fontSize: 12
						},
						rotate:0
					},
                    boundaryGap:true,
					axisLine: {
						show:true
					},
					splitLine:{
						show:false
					},
					'data': past_week_days
				}],
				yAxis: [{
					'type': 'value',
                    show:true,
					axisLine: {
						show:true
					},
					splitLine: {
						show: false,
					},
					axisLabel: {
					    show:true,
						textStyle: {
							color: '#878787',
							fontStyle: 'normal',
							fontWeight: 'normal',
							fontFamily: "IRANSans",
							fontSize: 12
						},

					},
				}],
				series:[{
					'name': 'رطوبت خاک',
					'type': 'line',
					'data': week_soil_moisture_avgs,
					itemStyle: {
						normal: {
							color: new echarts.graphic.LinearGradient(
								0, 1, 0, 0, [{
									offset: 0,
									color: '#208a5d'
								}, {
									offset: 1,
									color: '#154f57'
								}]
							),
							barBorderRadius: 4
						},
						emphasis: {
							color: new echarts.graphic.LinearGradient(
								0, 1, 0, 0, [{
									offset: 0,
									color: '#208a5d'
								}, {
									offset: 1,
									color: '#fff'
								}]
							),
							barBorderRadius: 4
						}
					},
					label: {
						normal: {
							show: true,
							position: 'top',
							formatter: '{c}',
							color: '#fff',
							fontStyle: 'normal',
							fontWeight: 'normal',
							fontFamily: "IRANSans",
							fontSize: 12
						}
					},
				}]
			}, {
				series: [{
					'data': week2_soil_moisture_avgs
				}]
			}, {
				series: [{
					'data': week3_soil_moisture_avgs
				}]
			}, {
				series: [{
					'data': week4_soil_moisture_avgs
				}]
			}, {
				series: [{
					'data': week5_soil_moisture_avgs
				}]
			}, {
				series: [{
					'data': week6_soil_moisture_avgs
				}]
			}, {
				series: [{
					'data': week7_soil_moisture_avgs
				}]
			}, {
				series: [{
					'data': week8_soil_moisture_avgs
				}]
			// }, {
			// 	series: [{
			// 		'data': [2, 40, 64, 134, 188, 43, 109, 12]
			// 	}]
			// },
			// {
			// 	series: [{
			// 		'data': [3, 40, 64, 134, 188, 43, 109, 12]
			// 	}]
			// }, {
			// 	series: [{
			// 		'data': [4, 6, 10, 28, 8, 24, 11, 16]
			// 	}]
			}, ]
		};
		console.log(soilvalue);
		soilmoisture.setOption(option3);
		soilmoisture.resize();
	}
}
var soilmoisture_momentary = function () {
		// if( $('#soilmoisture').length > 0 ){
		// var soilmoistureMomentary = echarts.init(document.getElementById('soilmoisture'));
        //
        //
		// var URL = "/sensorconditions/";
		// var soilMoistureData = [];
		// var now = new Date();
		// var tenMinutes = 10*60*1000;
		// var oneDay = 24 * 3600 * 1000;
		// var value = Math.random() * 1000;
		// var soilMoistureValue = [];
		// 	// $.getJSON(function(data){
		// 	//  if(data)
		// 	// 		{
		// 	// 			pushSoilMoistureData(data);
		// 	//
		// 	// 		}
		// 	//
		// 	// },URL);
		// $.ajax({
		// 		url: URL,
		// 		dataType: 'json',
        //
		// 		async: false,
		// 		success: function(data){
		// 			soilMoistureData.push(data[0].last_soil);
		// 			soilMoistureValue.push(data[0].last_soil.value);
		// 		}
		// 	});
		// //soilMoistureData.forEach( x => soilMoistureValue.push(x.value) );
        //
		//  var option_soilmoisture_momentary = {
		//      timeline:{
		//          show:false,
        //      },
		// 	title: {
		// 		text: 'رطوبت خاک',
		// 				show: false
		// 	},
		// 	tooltip: {
		// 		trigger: 'axis',
		// 		// formatter: function (params) {
		// 		// 	params = params[0];
		// 		// 	var date = new Date(params.name);
		// 						//return moment(date).locale('fa').format("jYYYY/jMM/jDD");
		// 			// return date.getDate() + '/' + (date.getMonth() + 1) + '/' + date.getFullYear() + ' : ' + params.value[1];
		// 					//	return date.getHours() + ':' + date.getMinutes()  + '/'  + params.value[1];
        //
		// 		//},
		// 		axisPointer: {
		// 			animation: false
		// 		}
		// 	},
		// 	xAxis: {
		// 		type: 'category',
        //
		// 				//distribution: 'series',
		// 		splitLine: {
		// 			show: false
		// 		},
		// 		axisLabel:{
		// 			formatter:function(data){
		// 			    console.log(data); debugger
		// 			return data.jalali_created.join();
		// 		},
		// 			interval: 0
		// 		},
        //         data:soilMoistureData,
        //
		// 	},
		// 	yAxis: {
		// 		type: 'value',
		// 		boundaryGap: [0, '100%'],
		// 		splitLine: {
		// 			show: false
		// 		}
		// 	},
		// 	series: [{
		// 		name: 'رطوبت خاک',
		// 		type: 'line',
		// 		showSymbol: false,
		// 		hoverAnimation: false,
		// 				itemStyle: {
		// 					normal: {
		// 						color: new echarts.graphic.LinearGradient(
		// 							0, 1, 0, 0, [{
		// 								offset: 0,
		// 								color: '#208a5d'
		// 							}, {
		// 								offset: 1,
		// 								color: '#154f57'
		// 							}]
		// 						),
		// 						barBorderRadius: 4
		// 					},
		// 					emphasis: {
		// 						color: new echarts.graphic.LinearGradient(
		// 							0, 1, 0, 0, [{
		// 								offset: 0,
		// 								color: '#208a5d'
		// 							}, {
		// 								offset: 1,
		// 								color: '#fff'
		// 							}]
		// 						),
		// 						barBorderRadius: 4
		// 					}
		// 				},
		// 		data: soilMoistureValue,
		// 	}]
		// };
        //
		// setInterval(function () {
        //
		// 	$.ajax({
		// 		url: URL,
		// 		dataType: 'json',
        //
		// 		async: false,
		// 		success: function(data){
		// 			soilMoistureData.push(data[0].last_soil);
		// 			soilMoistureValue.push(data[0].last_soil.value);
		// 			soilmoistureMomentary.setOption(option_soilmoisture_momentary);
		// 		}
		// 	});
		// 	// $.getJSON(function(data){
		// 	//  if(data)
		// 	// 		{
		// 	//
		// 	// 			soilMoistureData.push(data);
		// 	// 		}
		// 	//
		// 	// },URL);
		// 	// soilMoistureData.forEach( x => soilMoistureValue.push(x.value) );
        //
		// 	// for (var jd = 0; jd < 6; jd++) {
		// 	// 	var newData = getSoilMoistureData();
		// 	// 	//soilMoistureData.shift();
		// 	// 	if(newData){
		// 	// 			soilMoistureData.push(newData);
		// 	// 			soilMoistureData.forEach( x => soilMoistureValue.push(x.value) );
		// 	// 	}
		// 	//
		// 	// }
        //
		// 	// soilmoisture.setOption({
		// 	// 	series: [{
		// 	// 		data: soilMoistureValue
		// 	// 	}]
		// 	// });
		// }, tenMinutes);
		// 		soilmoistureMomentary.setOption(option_soilmoisture_momentary);
		// 		soilmoistureMomentary.resize();
		// 	}
    if( $('#soilmoisture').length > 0 ) {
			var soilmoisture = echarts.init(document.getElementById('soilmoisture'));
			soilMoistureChartXaxisFlag = "momentary";
			var URL = "/sensorconditions/";
            var soilMoistureData = [];
            var tenMinutes = 10*60*1000;
            var soilMoistureValue = [];
            var jalaliDates=[];
            var createdHours_minutes = [];
            var createdTime = new Date();
             // $.ajax({
             //        url: URL,
             //        dataType: 'json',
			 //
             //        async: false,
             //        success: function(data){
             //            soilMoistureData.push(data[0].last_soil);
             //            soilMoistureValue.push(data[0].last_soil.value);
             //            jalaliDates.push(data[0].last_soil.jalali_created.join());
             //            createdHours_minutes.push(moment(Date.parse(data[0].last_soil.created)).format('LT'));
             //        }
             //    });


			for(let i = daily_values.length - 1;i >= 0; i--){soilMoistureValue.push(daily_values[i][0])}
			for(let i = daily_values.length - 1;i >= 0; i--){createdHours_minutes.push(daily_values[i][1] + ',' + daily_values[i][2] + ',' + daily_values[i][3] + ' ' + daily_values[i][4] + ':' + daily_values[i][5])}

            const interval = setInterval(function()
            {
                if(soilMoistureChartXaxisFlag != "momentary")
                {
                    clearInterval(interval);
                }
                else{
                       $.ajax({
                    url: URL,
                    dataType: 'json',
                    async: false,
                    success: function(data){
                        soilMoistureData.push(data[0].last_soil);
                        soilMoistureValue.push(data[0].last_soil.value);
                        //jalaliDates.push(data[0].last_soil.jalali_created.join());
						var jtime = data[0].last_soil.jalali_created.join() + ' ' + moment(Date.parse(data[0].last_soil.created)).format('H:mm');
						createdHours_minutes.push(jtime);
                    }
                });
                	soilmoisture.setOption(option3);
			        soilmoisture.resize();
                }

            },tenMinutes);




			var option3 = {
				timeline:{
					show:false
				},
				options: [{
					tooltip: {
						trigger: 'axis',
						backgroundColor: 'rgba(33,33,33,1)',
						borderRadius: 0,
						padding: 10,
						textStyle: {
							color: '#fff',
							fontStyle: 'normal',
							fontWeight: 'normal',
							fontFamily: "IRANSans",
							fontSize: 12
						}
					},
					calculable: true,
					grid: {
						show: false
					},
					xAxis: [{
						'type': 'category',
						axisLabel: {
							interval:'auto',
							showMaxLabel: true,
							textStyle: {
								color: '#878787',
								fontStyle: 'normal',
								fontWeight: 'normal',
								//fontFamily: "IRANSans",
								fontSize: 12

							},
							rotate:0
						},
                        boundaryGap:false,
						axisLine: {
							show: true
						},
						splitLine: {
							show: false
						},
						'data': createdHours_minutes
					}],
					yAxis: [{
						'type': 'value',
                        show:true,
						axisLine: {
							show: true
						},
						axisLabel: {
							textStyle: {
								color: '#878787',
								fontStyle: 'normal',
								fontWeight: 'normal',
								fontFamily: "IRANSans",
								fontSize: 12
							}
						},
						splitLine: {
							show: false,
						},
					}],
					dataZoom: [
                            {
                            	startValue: ''
							},
							{
								type: 'inside'
							}],
					series: [{
						'name': 'رطوبت خاک',
						'type': 'line',
						'data': soilMoistureValue,
						itemStyle: {
							normal: {
								color: new echarts.graphic.LinearGradient(
									0, 1, 0, 0, [{
										offset: 0,
										color: '#208a5d'
									}, {
										offset: 1,
										color: '#154f57'
									}]
								),
								barBorderRadius: 4
							},
							emphasis: {
								color: new echarts.graphic.LinearGradient(
									0, 1, 0, 0, [{
										offset: 0,
										color: '#208a5d'
									}, {
										offset: 1,
										color: '#fff'
									}]
								),
								barBorderRadius: 4
							}
						},
						label: {
							normal: {
								show: true,
								position: 'top',
								formatter: '{c}',
								color: '#fff',
								fontStyle: 'normal',
								fontWeight: 'normal',
								fontFamily: "IRANSans",
								fontSize: 12
							}
						},
					}]
				}]
			};
			// console.log(soilvalue);
            soilmoisture.setOption(option3);
			        soilmoisture.resize();
		}
}

var temperature_monthly = function()
{
	if ( $('#temperaturSensor').length > 0)
	{
			var temperaturSensor = echarts.init(document.getElementById('temperaturSensor'));
		/*Defining Data*/

		var	tempOption = {
			// title: {
			//     text: 'دمای حداقل و حداکثر',
			//     //subtext: '纯属虚构'
			// },
			tooltip: {
				trigger: 'axis'
			},
			legend: {
				data: ['دمای حداقل', 'دمای حداکثر']
			},
			toolbox: {
				show: true,
				feature: {
					// dataZoom: {
					//     yAxisIndex: 'none'
					// },
					dataView: {readOnly: false},
					magicType: {type: ['line', 'bar']},
					//restore: {},
					//saveAsImage: {}
				}
			},
			xAxis: {
				type: 'category',
				axisLabel: {
							showMaxLabel: true,
							interval:3,
							textStyle: {
								color: '#878787',
								fontStyle: 'normal',
								fontWeight: 'normal',
								fontFamily: "IRANSans",
								fontSize: 12

							},
							rotate:90
						},
				boundaryGap: false,
				data: past_month_days
			},
			yAxis: {
				type: 'value',
				axisLabel: {
					formatter: '{value} °C'
				}
			},
			series: [
				{
					name: 'دمای حداکثر',
					type: 'line',
					data: month_max_temps,
                    smooth: true,
					markPoint: {
						data: [
							{type: 'max', name: 'دمای حداکثر'},
							{type: 'min', name: 'دمای حداقل'}
						]
					},
					markLine: {
						data: [
							{type: 'average', name: 'میانگین'}
						]
					}
				},
				{
					name: 'دمای حداقل',
					type: 'line',
					data: month_min_temps,
                    smooth: true,
					markPoint: {
						data: [
											{type: 'max', name: 'دمای حداکثر'},
											{type: 'min', name: 'دمای حداقل'}
							//{name: '周最低', value: -2, xAxis: 1, yAxis: -1.5}
						]
					},
					markLine: {
						data: [
							{type: 'average', name: 'میانگین'},
							// [{
							//     symbol: 'none',
							//     x: '90%',
							//     yAxis: 'max'
							// }, {
							//     symbol: 'circle',
							//     label: {
							//         position: 'start',
							//         formatter: '最大值'
							//     },
							//     type: 'max',
							//     name: '最高点'
							// }]
						]
					}
				}
			]
		};

		temperaturSensor.setOption(tempOption);


	}
	return false;
}

var temperature_weekly = function () {
		if( $('#temperaturSensor').length > 0 ) {


		var temperaturSensor = echarts.init(document.getElementById('temperaturSensor'));
		/*Defining Data*/

		var	tempOption = {
			// title: {
			//     text: 'دمای حداقل و حداکثر',
			//     //subtext: '纯属虚构'
			// },
			tooltip: {
				trigger: 'axis'
			},
			legend: {
				data: ['دمای حداقل', 'دمای حداکثر']
			},
			toolbox: {
				show: true,
				feature: {
					// dataZoom: {
					//     yAxisIndex: 'none'
					// },
					dataView: {readOnly: false},
					magicType: {type: ['line', 'bar']},
					//restore: {},
					//saveAsImage: {}
				}
			},
			xAxis: {
				type: 'category',

				axisLabel: {
				            interval:0,
							textStyle: {
								color: '#878787',
								fontStyle: 'normal',
								fontWeight: 'normal',
								fontFamily: "IRANSans",
								fontSize: 12

							},
							rotate:0
						},
				boundaryGap: false,
				data: past_week_days
			},
			yAxis: {
				type: 'value',
				axisLabel: {
					formatter: '{value} °C'
				},

			},
			series: [
				{
					name: 'دمای حداکثر',
					type: 'line',
					data: week_max_temps,
                    smooth: true,
					markPoint: {
						data: [
							{type: 'max', name: 'دمای حداکثر'},
							{type: 'min', name: 'دمای حداقل'}
						]
					},
					markLine: {
						data: [
							{type: 'average', name: 'میانگین'}
						]
					}
				},
				{
					name: 'دمای حداقل',
					type: 'line',
					data: week_min_temps,
                    smooth: true,
					markPoint: {
						data: [
											{type: 'max', name: 'دمای حداکثر'},
											{type: 'min', name: 'دمای حداقل'}
							//{name: '周最低', value: -2, xAxis: 1, yAxis: -1.5}
						]
					},
					markLine: {
						data: [
							{type: 'average', name: 'میانگین'},
							// [{
							//     symbol: 'none',
							//     x: '90%',
							//     yAxis: 'max'
							// }, {
							//     symbol: 'circle',
							//     label: {
							//         position: 'start',
							//         formatter: '最大值'
							//     },
							//     type: 'max',
							//     name: '最高点'
							// }]
						]
					}
				}
			]
		};

		temperaturSensor.setOption(tempOption);

	}
}


var lastwater_monthly = function()
{
		if( $('#lastwater').length > 0 ){
		var sumwater = echarts.init(document.getElementById('lastwater'));
        var	sumWaterOption = {
			// title: {
			//     text: 'دمای حداقل و حداکثر',
			//     //subtext: '纯属虚构'
			// },
			tooltip: {
				trigger: 'axis',

			},
			legend: {
				data: ['مصرف آب هوشمند', 'مصرف آب شاهد'],

			},
			toolbox: {
				show: true,
				feature: {
					// dataZoom: {
					//     yAxisIndex: 'none'
					// },
					dataView: {readOnly: false},
					magicType: {type: ['line', 'bar']},
					//restore: {},
					//saveAsImage: {}
				}
			},
			xAxis: {
				type: 'category',
				axisLabel: {
							showMaxLabel: true,
							interval:3,
							textStyle: {
								color: '#878787',
								fontStyle: 'normal',
								fontWeight: 'normal',
								fontFamily: "IRANSans",
								fontSize: 12

							},
							rotate:90
						},
				boundaryGap: false,
				data: past_month_days
			},
			yAxis: {
			    show:true,
				type: 'value',
                scale: true,
                axisLine:{
			        show:true,
                },
				axisLabel: {
			        margin: 5,
					formatter: '{value} '
				}
			},
			series: [
				{
					name: 'مصرف آب شاهد',
					type: 'line',
                    itemStyle: {
          normal: {
            color: '#154f57',
            shadowBlur: 5,
            shadowColor: 'rgba(0, 0, 0, .2)'
          }
        },
                    smooth:true,
                    silent: true,
                    //barWidth: 6,
                    barGap: '0%',
					data: last_water_samples_monthly,
					markPoint: {
						data: [
							{type: 'max', name: 'حداکثر مصرف آب'},
							{type: 'min', name: 'حداقل مصرف آب'}
						]
					},
					markLine: {
						data: [
							{type: 'average', name: 'میانگین'}
						]
					}
				},
				{
					name: 'مصرف آب هوشمند',
					type: 'line',
					itemStyle: {
          normal: {
            color: '#208a5d',
            shadowBlur: 5,
            shadowColor: 'rgba(0, 0, 0, .5)'
          }
        },
                    smooth:true,
                    //barWidth: 6,
                    z: 10,
                    data: last_water_originals_monthly,
					markPoint: {
						data: [
											{type: 'max', name: 'حداکثر مصرف آب'},
											{type: 'min', name: 'حداقل مصرف آب'}
							//{name: '周最低', value: -2, xAxis: 1, yAxis: -1.5}
						]
					},
					markLine: {
						data: [
							{type: 'average', name: 'میانگین'},
							// [{
							//     symbol: 'none',
							//     x: '90%',
							//     yAxis: 'max'
							// }, {
							//     symbol: 'circle',
							//     label: {
							//         position: 'start',
							//         formatter: '最大值'
							//     },
							//     type: 'max',
							//     name: '最高点'
							// }]
						]
					}
				}
			]
		};

    // var barGaps = ['30%', '-100%'];
    // var loopIndex = 0;
	//
    // setInterval(function () {
    //   var barGap = barGaps[loopIndex];
	//
    //   sumwater.setOption({
    //     xAxis: {
	// 				//data: ['شنبه', 'یکشنبه', 'دوشنبه', 'سه شنبه', 'چهارشنبه', 'پنج شنبه', 'جمعه'],
    //       // axisLabel: {
    //       //   rotate:90
    //       // }
    //     },
    //     series: [{
    //       barGap: barGap
    //     }]
    //   });
    //   loopIndex = (loopIndex + 1) % barGaps.length;
	//
    // }, 2000);

    sumwater.setOption(sumWaterOption);

	}


}

var lastwater_weekly = function () {
		if( $('#lastwater').length > 0 ){
		var sumwater = echarts.init(document.getElementById('lastwater'));
    // var option = {
    //   xAxis: {
    //     data: past_week_days,
    //     axisTick: {show: true},
    //     axisLine: {
    //       show:true
    //     },
    //     axisLabel: {
    //   //    formatter: 'barGap: \'-100%\'',
    //       textStyle: {
    //         color: '#878787',
    //         fontStyle: 'normal',
    //         fontWeight: 'normal',
    //         fontFamily: "'Montserrat', sans-serif",
    //         fontSize: 12
    //       },
	// 		rotate:0
    //     }
    //
    //   },
    //   yAxis: {
    //     splitLine: {show: false},
    //     axisLine: {
    //       show:false
    //     },
    //     axisLabel: {
    //       textStyle: {
    //         color: '#878787',
    //         fontStyle: 'normal',
    //         fontWeight: 'normal',
    //         fontFamily: "'Montserrat', sans-serif",
    //         fontSize: 12
    //       }
    //     }
    //   },
    //   animationDurationUpdate: 1200,
    //   series: [{
    //     type: 'bar',
    //     itemStyle: {
    //       normal: {
    //         color: '#154f57',
    //         shadowBlur: 5,
    //         shadowColor: 'rgba(0, 0, 0, .2)'
    //       }
    //     },
    //     silent: true,
    //     barWidth: 20,
    //     barGap: '-100%', // Make series be overlap
    //     data: sum_water_originals
    //   }, {
    //     type: 'bar',
    //     itemStyle: {
    //       normal: {
    //         color: '#208a5d',
    //         shadowBlur: 5,
    //         shadowColor: 'rgba(0, 0, 0, .5)'
    //       }
    //     },
    //     barWidth: 40,
    //     z: 10,
    //     data: sum_water_samples
    //   }]
    // };
    var	sumWaterOption = {
			// title: {
			//     text: 'دمای حداقل و حداکثر',
			//     //subtext: '纯属虚构'
			// },
			tooltip: {
				trigger: 'axis',
                formatter:'{b}</br>{a0} : {c0} لیتر</br>{a1} : {c1} لیتر'

			},
			legend: {
				data: ['مصرف آب هوشمند', 'مصرف آب شاهد'],

			},
			toolbox: {
				show: true,
				feature: {
					// dataZoom: {
					//     yAxisIndex: 'none'
					// },
					dataView: {readOnly: false},
					magicType: {type: ['line', 'bar']},
					//restore: {},
					//saveAsImage: {}
				}
			},
			xAxis: {
				type: 'category',
				axisLabel: {
							showMaxLabel: true,
							interval:'auto',
							textStyle: {
								color: '#878787',
								fontStyle: 'normal',
								fontWeight: 'normal',
								fontFamily: "IRANSans",
								fontSize: 12

							},
							rotate:0
						},
				boundaryGap: true,
				data: past_week_days
			},
			yAxis: {
			    show:true,
				type: 'value',
                scale: true,
                axisLine:{
			        show:true,
                },
				axisLabel: {
			        margin: 5,
					formatter: '{value} '
				}
			},
            animationDurationUpdate: 1200,
			series: [
				{
					name: 'مصرف آب شاهد',
					type: 'bar',
                    itemStyle: {
          normal: {
            color: '#154f57',
            shadowBlur: 5,
            shadowColor: 'rgba(0, 0, 0, .2)'
          }
        },
                    smooth:true,
                    silent: true,
                    //barWidth: 25,
                    barGap: '0%', // Make series be overlap
					data: last_water_samples,
					markPoint: {
						data: [
							{type: 'max', name: 'حداکثر مصرف آب'},
							{type: 'min', name: 'حداقل مصرف آب'}
						]
					},
					markLine: {
						data: [
							{type: 'average', name: 'میانگین'}
						]
					}
				},
				{
					name: 'مصرف آب هوشمند',
					type: 'bar',
					itemStyle: {
          normal: {
            color: '#208a5d',
            shadowBlur: 5,
            shadowColor: 'rgba(0, 0, 0, .5)'
          }
        },
                    smooth:true,
                   // barWidth: 25,
                    z: 10,
                    data: last_water_originals,
					markPoint: {
						data: [
											{type: 'max', name: 'حداکثر مصرف آب'},
											{type: 'min', name: 'حداقل مصرف آب'}
							//{name: '周最低', value: -2, xAxis: 1, yAxis: -1.5}
						]
					},
					markLine: {
						data: [
							{type: 'average', name: 'میانگین'},
							// [{
							//     symbol: 'none',
							//     x: '90%',
							//     yAxis: 'max'
							// }, {
							//     symbol: 'circle',
							//     label: {
							//         position: 'start',
							//         formatter: '最大值'
							//     },
							//     type: 'max',
							//     name: '最高点'
							// }]
						]
					}
				}
			]
		};

    // var barGaps = ['30%', '-100%'];
    // var loopIndex = 0;
	//
    // setInterval(function () {
    //   var barGap = barGaps[loopIndex];
	//
    //   sumwater.setOption({
    //     xAxis: {
	// 				//data: ['شنبه', 'یکشنبه', 'دوشنبه', 'سه شنبه', 'چهارشنبه', 'پنج شنبه', 'جمعه'],
    //       // axisLabel: {
    //       //   formatter: 'barGap: \'' + barGap + '\''
    //       // }
    //     },
    //     series: [{
    //       barGap: barGap
    //     }]
    //   });
    //   loopIndex = (loopIndex + 1) % barGaps.length;
	//
    // }, 2000);

    sumwater.setOption(sumWaterOption);

	}
}



var gdds_monthly = function()
{
	if( $('#gddchart').length > 0 ) {
		var gddchart = echarts.init(document.getElementById('gddchart'));
		//data
		var data = monthly_gdds;
		var markLineData = [];
		for (var i = 1; i < data.length; i++) {
			markLineData.push([{
				xAxis: i - 1,
				yAxis: data[i - 1],
				value: (data[i] - data[i - 1]).toFixed(2)
			}, {
				xAxis: i,
				yAxis: data[i]
			}]);
		}

		//option
		var option = {
			tooltip: {
				trigger: 'axis',
				backgroundColor: 'rgba(33,33,33,1)',
				borderRadius: 0,
				padding: 10,
				axisPointer: {
					type: 'line',
					label: {
						backgroundColor: 'rgba(33,33,33,1)'
					}
				},
				textStyle: {
					color: '#fff',
					fontStyle: 'normal',
					fontWeight: 'normal',
					fontFamily: "'Montserrat', sans-serif",
					fontSize: 12
				}
			},
			color: ['#154f57'],
			// grid: {
			// 	show: false,
			// 	top: 100,
			// 	bottom: 10,
			// 	containLabel: true,
			// },
			xAxis: {
				data: past_month_days,
				axisLine: {
					show:true,
				},
				axisLabel: {
							showMaxLabel: true,
							interval:3,
							textStyle: {
								color: '#878787',
								fontStyle: 'normal',
								fontWeight: 'normal',
								fontFamily: "IRANSans",
								fontSize: 12

							},
							rotate:90
						},
                axisTick: {
                  alignWithLabel: true,
                }

			},
			yAxis: {
				axisLine: {
					show: true
				},
				axisLabel: {
					textStyle: {
						color: '#878787'
					}
				},
				splitLine: {
					show: false,
				},
			},
			series: [{
				type: 'line',
				data: data,
				markPoint: {
					data: [
						{type: 'max', name: 'بیشترین'},
						// {type: 'min', name: 'کمترین'}
					]
				},
				markLine: {
					smooth: true,
					effect: {
						show: true
					},
					distance: 10,
					label: {
						normal: {
							position: 'middle'
						}
					},
					symbol: ['none', 'none'],
					data: markLineData
				}
			}]
		};
		gddchart.setOption(option);
		gddchart.resize();
	}
	return false;
}

var gdds_weekly = function()
{
	if( $('#gddchart').length > 0 ){
    	var gddchart = echarts.init(document.getElementById('gddchart'));
    	//data
		var data = gdds;
		var markLineData = [];
		for (var i = 1; i < data.length; i++) {
		  markLineData.push([{
			xAxis: i - 1,
			yAxis: data[i - 1],
			value: (data[i] - data[i-1]).toFixed(2)
		  }, {
			xAxis: i,
			yAxis: data[i]
		  }]);
		}

		//option
		var option = {
			tooltip: {
				trigger: 'axis',
				 backgroundColor: 'rgba(33,33,33,1)',
				// borderRadius:0,
				 padding:10,
				axisPointer: {
				  type: 'line',
				  label: {
					backgroundColor: 'rgba(33,33,33,1)'
				  }
				},
				textStyle: {
				  color: '#fff',
				  fontStyle: 'normal',
				  fontWeight: 'normal',
				  fontFamily: "'Montserrat', sans-serif",
				  fontSize: 12
				}
			},
			color: ['#154f57'],
			// grid:{
			// 	show:false,
			// 	top: 100,
			// 	bottom: 10,
			// 	containLabel: true,
			// },
			xAxis: {
				data: past_week_days,
				axisLine: {
					show:true
				},
				axisLabel: {
				            interval:0,
							textStyle: {
								color: '#878787',
								fontStyle: 'normal',
								fontWeight: 'normal',
								fontFamily: "IRANSans",
								fontSize: 12

							},
							rotate:0
						},
                axisTick: {
                  alignWithLabel: true,
                }
			},
			yAxis: {
			    show:true,
				axisLine: {
					show:true,
				},
				axisLabel: {
				    show:true,
					textStyle: {
						color: '#878787'
					}
				},
				splitLine: {
					show: false,
				},
			},
			series: [{
				type: 'line',
				data:data,
				markPoint: {
				  data: [
					{type: 'max', name: 'بالاترین ضریب'},
					// {type: 'min', name: '最小值'}
				  ]
				},
				markLine: {
				  smooth: true,
					  effect: {
						show: true
					  },
					  distance: 10,
				  label: {
					normal: {
					  position: 'middle'
					}
				  },
				  symbol: ['none', 'none'],
				  data: markLineData
				}
			}]
		};

    	gddchart.setOption(option);
    	gddchart.resize();
  	}
}









//$('#toggle-spout').
/*****Function Call start*****/
sparklineLogin();
echartsConfig();
/*****Function Call end*****/
