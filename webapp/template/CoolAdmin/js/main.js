$(document).ready(function() {
  (function ($) {
    // USE STRICT
    "use strict";

    try {

      // Percent Chart
      var ctx = document.getElementById("percent-chart");
      if (ctx) {
        ctx.height = 200;
        var myChart = new Chart(ctx, {
          type: 'pie',
          data: {
            datasets: [
              {
                label: "Hours distribution",
                data: [percentage_last_month_peak, percentage_last_month_off_peak, percentage_last_month_super_off_peak],
                backgroundColor: [
                  '#00b5e9',
                  '#fa4251',
                  '#00ad5f'
                ],
                hoverBackgroundColor: [
                  '#00b5e9',
                  '#fa4251',
                  '#00ad5f'

                ],
                borderWidth: [
                  5, 5, 5
                ],
                hoverBorderColor: [
                  'transparent',
                  'transparent',
                  'transparent'
                ]
              },
                {
                label: "Cost distribution",
                data: [percentage_last_month_peak_cost, percentage_last_month_off_peak_cost, percentage_last_month_super_off_peak_cost],
                backgroundColor: [
                  '#00b5e9',
                  '#fa4251',
                  '#00ad5f'
                ],
                hoverBackgroundColor: [
                  '#00b5e9',
                  '#fa4251',
                  '#00ad5f'

                ],
                borderWidth: [
                  5, 5, 5
                ],
                hoverBorderColor: [
                  'transparent',
                  'transparent',
                  'transparent'
                ]
              }
            ],
            labels: [
              'Peak',
              'Off-Peak',
              'Super-Peak'
            ]
          },
          options: {
            maintainAspectRatio: false,
            responsive: true,
            animation: {
              animateScale: true,
              animateRotate: true
            },
            legend: {
              display: false
            },
            tooltips: {
              titleFontFamily: "Poppins",
              xPadding: 15,
              yPadding: 10,
              caretPadding: 0,
              bodyFontSize: 16
            }
          }
        });
      }
      } catch (error) {
      console.log(error);
    }

    try{
      // Percent Chart
      var ctx2 = document.getElementById("percent-chart-2");
      if (ctx2) {
        ctx2.height = 280;
        var myChart = new Chart(ctx2, {
          type: 'pie',
          data: {
            datasets: [
              {
                label: "My First dataset",
                data: [percentage_last_month_peak_cost, percentage_last_month_off_peak_cost,
                  percentage_last_month_super_off_peak_cost],
                backgroundColor: [
                  '#00b5e9',
                  '#fa4251',
                  '#00ad5f'
                ],
                hoverBackgroundColor: [
                  '#00b5e9',
                  '#fa4251',
                  '#00ad5f'

                ],
                borderWidth: [
                  0, 0, 0
                ],
                hoverBorderColor: [
                  'transparent',
                  'transparent',
                  'transparent'
                ]
              }
            ],
            labels: [
              'Peak',
              'Off-Peak',
              'Super-Peak'
            ]
          },
          options: {
            maintainAspectRatio: false,
            responsive: true,
            cutoutPercentage: 55,
            animation: {
              animateScale: true,
              animateRotate: true
            },
            legend: {
              display: false
            },
            tooltips: {
              titleFontFamily: "Poppins",
              xPadding: 15,
              yPadding: 10,
              caretPadding: 0,
              bodyFontSize: 16
            }
          }
        });
      }

    } catch (error) {
      console.log(error);
    }



    try {
      //Sales chart
      var ctx = document.getElementById("overview-month-chart");
      if (ctx) {

        var myChart = new Chart(ctx, {
          type: 'line',
          data: {
            type: 'line',
            defaultFontFamily: 'Poppins',
            datasets: datasets_overview_month
          },
          options: {

            responsive: true,
            tooltips: false,
            legend: {
              display: true,
              labels: {
                usePointStyle: true,
                fontFamily: 'Poppins',
              },
            },
            scales: {
              xAxes: [{
                display: true,
                type: "time",

                time: {
                  format: "MM-DD-YYYY",
                  unit: "day",
                },
                gridLines: {
                  display: false,
                  drawBorder: false
                },
                scaleLabel: {
                  display: false,
                  labelString: 'Day of the Month'
                },
                ticks: {
                  fontFamily: "Poppins"
                }
              }],
              yAxes: [{
                display: true,
                gridLines: {
                  display: false,
                  drawBorder: false
                },
                scaleLabel: {
                  display: true,
                  labelString: 'Mean Power Spent [kW]',
                  fontFamily: "Poppins"

                },
                ticks: {
                  fontFamily: "Poppins"
                }
              }]
            },
            title: {
              display: false,
              text: 'Normal Legend'
            }
          }
        });
      }


    } catch (error) {
      console.log(error);
    }

        try {
      //Sales chart
      var ctx = document.getElementById("overview-period-chart");
      if (ctx) {

        var myChart = new Chart(ctx, {
          type: 'line',
          data: {
            type: 'line',
            defaultFontFamily: 'Poppins',
            datasets: datasets_overview_month
          },
          options: {

            responsive: true,
            tooltips: false,
            legend: {
              display: true,
              labels: {
                usePointStyle: true,
                fontFamily: 'Poppins',
              },
            },
            scales: {
              xAxes: [{
                display: true,
                type: "time",

                time: {
                  format: "MM-DD-YYYY",
                  unit: "day",
                },
                gridLines: {
                  display: false,
                  drawBorder: false
                },
                scaleLabel: {
                  display: false,
                  labelString: 'Day of the Month'
                },
                ticks: {
                  fontFamily: "Poppins"
                }
              }],
              yAxes: [{
                display: true,
                gridLines: {
                  display: false,
                  drawBorder: false
                },
                scaleLabel: {
                  display: false,
                  labelString: 'Mean Power Spent [kW]',
                  fontFamily: "Poppins"

                },
                ticks: {
                  fontFamily: "Poppins"
                }
              }]
            },
            title: {
              display: false,
              text: 'Normal Legend'
            }
          }
        });
      }


    } catch (error) {
      console.log(error);
    }


    try {
      //power + reneals chart
      var ctx = document.getElementById("power-renewals-chart");
      if (ctx) {
        ctx.height = 150;
        var myChart = new Chart(ctx, {
          type: 'line',
          data: {
            labels: x_axis,
            type: 'line',
            defaultFontFamily: 'Poppins',
            datasets: [{
              label: 'Without Panels and Batteries',
              data: total_load,
              backgroundColor: 'transparent',
              borderColor: 'rgba(220,53,69,0.75)',
              borderWidth: 3,
              pointStyle: 'circle',
              pointRadius: 5,
              pointBorderColor: 'transparent',
              pointBackgroundColor: 'rgba(220,53,69,0.75)',
            }, {
              label: "With Panels and Batteries",
              data: load_from_grid,
              backgroundColor: 'transparent',
              borderColor: 'rgba(40,167,69,0.75)',
              borderWidth: 3,
              pointStyle: 'circle',
              pointRadius: 5,
              pointBorderColor: 'transparent',
              pointBackgroundColor: 'rgba(40,167,69,0.75)',
            }]
          },
          options: {
            responsive: true,
            tooltips: {
              mode: 'index',
              titleFontSize: 12,
              titleFontColor: '#000',
              bodyFontColor: '#000',
              backgroundColor: '#fff',
              titleFontFamily: 'Poppins',
              bodyFontFamily: 'Poppins',
              cornerRadius: 3,
              intersect: false,
            },
            legend: {
              display: true,
              position: "top",
              labels: {
                usePointStyle: true,
                fontFamily: 'Poppins',
              },
            },
            scales: {
              xAxes: [{
                display: true,
                gridLines: {
                  display: false,
                  drawBorder: false
                },
                scaleLabel: {
                  display: true,
                  labelString: 'Hour of the Day'
                },
                ticks: {
                  fontFamily: "Poppins"
                }
              }],
              yAxes: [{
                display: true,
                gridLines: {
                  display: false,
                  drawBorder: false
                },
                scaleLabel: {
                  display: true,
                  labelString: 'Total Power Spent (normalized)',
                  fontFamily: "Poppins"

                },
                ticks: {
                  fontFamily: "Poppins"
                }
              }]
            },
            title: {
              display: false,
              text: 'Normal Legend'
            }
          }
        });
      }


    } catch (error) {
      console.log(error);
    }
    try {
      //bar chart
      var ctx = document.getElementById("bar-renewals-chart");
      if (ctx) {
        ctx.height = 150;
        var myChart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: x_axis,
            defaultFontFamily: 'Poppins',
            datasets: [{
              label: 'waisted PV generation',
              data: generated_PV_waisted,
              backgroundColor: 'rgba(220,53,69,0.75)',
            }, {
              label: 'used PV generation',
              data: generated_PV_used,
              backgroundColor: 'rgba(50,253,69,0.75)',
            }, {
              label: 'used from batteries',
              data: battery_used,
              backgroundColor: 'rgba(50,50,250,0.75)',
            }]
          },
          options: {
            responsive: true,
            tooltips: {
              mode: 'index',
              titleFontSize: 12,
              titleFontColor: '#000',
              bodyFontColor: '#000',
              backgroundColor: '#fff',
              titleFontFamily: 'Poppins',
              bodyFontFamily: 'Poppins',
              cornerRadius: 3,
              intersect: false,
            },
            legend: {
              display: true,
              labels: {
                usePointStyle: true,
                fontFamily: 'Poppins',
              },
            },
            scales: {
              xAxes: [{
              	stacked: true,
                display: true,
                gridLines: {
                  display: false,
                  drawBorder: false
                },
                scaleLabel: {
                  display: true,
                  labelString: 'Hour of the Day'
                },
                ticks: {
                  fontFamily: "Poppins"
                }
              }],
              yAxes: [{
                stacked: true,
                display: true,
                gridLines: {
                  display: false,
                  drawBorder: false
                },
                scaleLabel: {
                  display: true,
                  labelString: 'Power [kW]',
                  fontFamily: "Poppins"

                },
                ticks: {
                  fontFamily: "Poppins"
                }
              }]
            },
            title: {
              display: false,
              text: 'Normal Legend'
            }
          }
        });
      }


    } catch (error) {
      console.log(error);
    }
    try {
      //savings chart
      var ctx = document.getElementById("overview-pv-savings");
      if (ctx) {
        ctx.height = 150;
        var myChart = new Chart(ctx, {
          type: 'line',
          data: {
            type: 'line',
            defaultFontFamily: 'Poppins',
            datasets: pv_and_bat_data_xy_dic
          },
          options: {
            responsive: true,
            tooltips: false,
            legend: {
              display: true,
              labels: {
                usePointStyle: true,
                fontFamily: 'Poppins',
              },
            },
            scales: {
              xAxes: [{
                type: 'linear',
                display: true,
                gridLines: {
                  display: false,
                  drawBorder: false
                },
                scaleLabel: {
                  display: true,
                  labelString: 'Investment [€]'
                },
                ticks: {
                  fontFamily: "Poppins"
                }
              }],
              yAxes: [{
                display: true,
                gridLines: {
                  display: false,
                  drawBorder: false
                },
                scaleLabel: {
                  display: true,
                  labelString: 'Pay Back Period [Years]',
                  fontFamily: "Poppins"

                },
                ticks: {
                  fontFamily: "Poppins"
                }
              }]
            },
            title: {
              display: false,
              text: 'Normal Legend'
            }
          }
        });
      }


    } catch (error) {
      console.log(error);
    }

    try {

      //Team chart
      var ctx = document.getElementById("power-mean-month");
      if (ctx) {
        ctx.height = 150;
        var myChart = new Chart(ctx, {
          type: 'line',
          data: {
            labels: power_spent_by_hours_label,
            type: 'line',
            defaultFontFamily: 'Poppins',
            datasets: [{
              data: power_loader_meter_hours_max,
              label: "Maximum Power Spent [kW]",
              backgroundColor: 'rgba(0,103,255,.15)',
              borderColor: 'rgba(0,103,255,0.5)',
              borderWidth: 3.5,
              pointStyle: 'circle',
              pointRadius: 5,
              pointBorderColor: 'transparent',
              pointBackgroundColor: 'rgba(0,103,255,0.5)',
            },]
          },
          options: {
            responsive: true,
            tooltips: {
              mode: 'index',
              titleFontSize: 12,
              titleFontColor: '#000',
              bodyFontColor: '#000',
              backgroundColor: '#fff',
              titleFontFamily: 'Poppins',
              bodyFontFamily: 'Poppins',
              cornerRadius: 3,
              intersect: false,
            },
            legend: {
              display: false,
              position: 'top',
              labels: {
                usePointStyle: true,
                fontFamily: 'Poppins',
              },


            },
            scales: {
              xAxes: [{
                display: true,
                gridLines: {
                  display: false,
                  drawBorder: false
                },
                scaleLabel: {
                  display: true,
                  labelString: 'Hour of the Day'
                },
                ticks: {
                  fontFamily: "Poppins"
                }
              }],
              yAxes: [{
                display: true,
                gridLines: {
                  display: false,
                  drawBorder: false
                },
                scaleLabel: {
                  display: true,
                  labelString: 'Maximum Power Spent [kW]',
                  fontFamily: "Poppins"
                },
                ticks: {
                  fontFamily: "Poppins"
                }
              }]
            },
            title: {
              display: false,
            }
          }
        });
      }


    } catch (error) {
      console.log(error);
    }



    try {

      //Team chart
      var ctx = document.getElementById("contract-by-month");
      if (ctx) {
        ctx.height = 150;
        var myListOfDatasets = [{
              data: max_contract_power_by_month,
              label: "Max Power Spent [kW]",
              backgroundColor: 'rgba(0,103,255,.15)',
              borderColor: 'rgba(0,103,255,0.5)',
              borderWidth: 3.5,
              pointStyle: 'circle',
              pointRadius: 5,
              pointBorderColor: 'transparent',
              pointBackgroundColor: 'rgba(0,103,255,0.5)',
            },
          {   data: contracted_power_values,
              label: "Current Contract " + label_current_contract,
              backgroundColor: 'transparent',
              borderColor: 'rgba(255,26,0,0.5)',
              borderWidth: 3.5,
              pointStyle: 'circle',
              pointRadius: 0,
              pointBorderColor: 'transparent',
              pointBackgroundColor: 'rgba(255,26,0,0.5)',
            }];
        var i;
        for (i = 0; i < contracted_powers_perc_values.length; i++) {
            myListOfDatasets.push({
                  data: contracted_powers_perc_values[i],
                  label: contracted_powers_perc_label[i],
                  borderColor: 'rgba(0,161,2,0.5)',
                  backgroundColor: 'transparent',
                  borderWidth: 3.5,
                  pointStyle: 'circle',
                  pointRadius: 0,
                  pointBorderColor: 'transparent',
                  pointBackgroundColor: 'rgba(0,161,2,0.5)',
              })
        }

        var myChart = new Chart(ctx, {
          type: 'line',
          data: {
            labels: labels_contract_power_by_month,
            type: 'line',
            defaultFontFamily: 'Poppins',
            datasets: myListOfDatasets,
          },
          options: {
            responsive: true,
            tooltips: {
              mode: 'index',
              titleFontSize: 12,
              titleFontColor: '#000',
              bodyFontColor: '#000',
              backgroundColor: '#fff',
              titleFontFamily: 'Poppins',
              bodyFontFamily: 'Poppins',
              cornerRadius: 3,
              intersect: false,
            },
            legend: {
              display: true,
              position: 'top',
              labels: {
                usePointStyle: true,
                fontFamily: 'Poppins',
              },


            },
            scales: {
              xAxes: [{
                display: true,
                gridLines: {
                  display: false,
                  drawBorder: false
                },
                scaleLabel: {
                  display: false,
                  labelString: 'Month'
                },
                ticks: {
                  fontFamily: "Poppins"
                }
              }],
              yAxes: [{
                display: true,
                gridLines: {
                  display: false,
                  drawBorder: false
                },
                scaleLabel: {
                  display: true,
                  labelString: 'Power Spent [kW]',
                  fontFamily: "Poppins"
                },
                ticks: {
                  fontFamily: "Poppins"
                }
              }]
            },
            title: {
              display: false,
            }
          }
        });
      }


    } catch (error) {
      console.log(error);
    }

    try {
      //bar chart
      var ctx = document.getElementById("barChart");
      if (ctx) {
        var myChart = new Chart(ctx, {
          type: 'bar',
          defaultFontFamily: 'Poppins',
          data: {
            labels: bar_plot_labels,
            datasets: [
              {
                label: "Cost",
                data: bar_plot_values,
                borderColor: "rgba(0, 123, 255, 0.9)",
                borderWidth: "0",
                backgroundColor: "rgba(0, 123, 255, 0.5)",
                fontFamily: "Poppins"
              }
            ]
          },
          options: {
            maintainAspectRatio: true,
            legend: {
              display: false
            },
            scales: {
              xAxes: [{
                ticks: {
                  fontFamily: "Poppins"
                }
              }],
              yAxes: [{
                ticks: {
                  beginAtZero: true,
                  fontFamily: "Poppins"
                },
                scaleLabel: {
                  display: true,
                  labelString: 'Cost [€]',
                  fontFamily: "Poppins",
                }
              }]
            }
          }
        });
      }


    } catch (error) {
      console.log(error);
    }

    try {
      //bar chart
      var ctx = document.getElementById("appliancesbarChart");
      if (ctx) {
        var myChart = new Chart(ctx, {
          type: 'bar',
          defaultFontFamily: 'Poppins',
          data: {
            labels: appliances_label,
            datasets: [
              {
                label: "Cost",
                data: appliances_data,
                borderColor: "rgba(0, 123, 255, 0.9)",
                borderWidth: "0",
                backgroundColor: "rgba(0, 123, 255, 0.5)",
                fontFamily: "Poppins"
              }
            ]
          },
          options: {
            maintainAspectRatio: false,
            legend: {
              display: false
            },
            scales: {
              xAxes: [{
                ticks: {
                  fontFamily: "Poppins"

                }
              }],
              yAxes: [{
                ticks: {
                  beginAtZero: true,
                  fontFamily: "Poppins"
                }
              }]
            }
          }
        });
      }


    } catch (error) {
      console.log(error);
    }

    try {

      // single bar chart
      var ctx = document.getElementById("tariff_months");
      if (ctx) {
        var myChart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: months_tariff_label,
            datasets: [
              {
                label: "Simple Tariff",
                data: simple_tariff_cross_months,
                borderColor: "rgba(0, 123, 255, 0.9)",
                borderWidth: "0",
                backgroundColor: "rgba(0, 123, 255, 0.5)"
              },
                {
                label: "Two-Period Tariff",
                data: two_tariff_cross_months,
                borderColor: "rgba(0,161,2,0.9)",
                borderWidth: "0",
                backgroundColor: "rgba(0,161,2, 0.5)"
              },
                {
                label: "Three Period Tariff",
                data: three_tariff_cross_months,
                borderColor: "rgba(255,26,0,0.9)",
                borderWidth: "0",
                backgroundColor: "rgba(255,26,0, 0.5)"
              }
            ]
          },
          options: {
            legend: {
              position: 'top',
              labels: {
                fontFamily: 'Poppins'
              }

            },
            scales: {
              xAxes: [{
                ticks: {
                  fontFamily: "Poppins",

                }
              }],
              yAxes: [{
                ticks: {
                  beginAtZero: true,
                  fontFamily: "Poppins",
                },
                scaleLabel: {
                  display: true,
                  labelString: 'Cost [€]',
                  fontFamily: "Poppins",
                }
              }]
            }
          }
        });
      }

    } catch (error) {
      console.log(error);
    }

  })(jQuery);

  (function ($) {
    // Use Strict
    "use strict";
    try {
      var progressbarSimple = $('.js-progressbar-simple');
      progressbarSimple.each(function () {
        var that = $(this);
        var executed = false;
        $(window).on('load', function () {

          that.waypoint(function () {
            if (!executed) {
              executed = true;
              /*progress bar*/
              that.progressbar({
                update: function (current_percentage, $this) {
                  $this.find('.js-value').html(current_percentage + '%');
                }
              });
            }
          }, {
            offset: 'bottom-in-view'
          });

        });
      });
    } catch (err) {
      console.log(err);
    }
  })(jQuery);
  (function ($) {
    // USE STRICT
    "use strict";

    // Scroll Bar
    try {
      var jscr1 = $('.js-scrollbar1');
      if (jscr1[0]) {
        const ps1 = new PerfectScrollbar('.js-scrollbar1');
      }

      var jscr2 = $('.js-scrollbar2');
      if (jscr2[0]) {
        const ps2 = new PerfectScrollbar('.js-scrollbar2');

      }

    } catch (error) {
      console.log(error);
    }

  })(jQuery);
  (function ($) {
    // USE STRICT
    "use strict";

    // Select 2
    try {

      $(".js-select2").each(function () {
        $(this).select2({
          minimumResultsForSearch: 20,
          dropdownParent: $(this).next('.dropDownSelect2')
        });
      });

    } catch (error) {
      console.log(error);
    }


  })(jQuery);
  (function ($) {
    // USE STRICT
    "use strict";

    // Dropdown
    try {
      var menu = $('.js-item-menu');
      var sub_menu_is_showed = -1;

      for (var i = 0; i < menu.length; i++) {
        $(menu[i]).on('click', function (e) {
          e.preventDefault();
          $('.js-right-sidebar').removeClass("show-sidebar");
          if (jQuery.inArray(this, menu) == sub_menu_is_showed) {
            $(this).toggleClass('show-dropdown');
            sub_menu_is_showed = -1;
          } else {
            for (var i = 0; i < menu.length; i++) {
              $(menu[i]).removeClass("show-dropdown");
            }
            $(this).toggleClass('show-dropdown');
            sub_menu_is_showed = jQuery.inArray(this, menu);
          }
        });
      }
      $(".js-item-menu, .js-dropdown").click(function (event) {
        event.stopPropagation();
      });

      $("body,html").on("click", function () {
        for (var i = 0; i < menu.length; i++) {
          menu[i].classList.remove("show-dropdown");
        }
        sub_menu_is_showed = -1;
      });

    } catch (error) {
      console.log(error);
    }

    var wW = $(window).width();
    // Right Sidebar
    var right_sidebar = $('.js-right-sidebar');
    var sidebar_btn = $('.js-sidebar-btn');

    sidebar_btn.on('click', function (e) {
      e.preventDefault();
      for (var i = 0; i < menu.length; i++) {
        menu[i].classList.remove("show-dropdown");
      }
      sub_menu_is_showed = -1;
      right_sidebar.toggleClass("show-sidebar");
    });

    $(".js-right-sidebar, .js-sidebar-btn").click(function (event) {
      event.stopPropagation();
    });

    $("body,html").on("click", function () {
      right_sidebar.removeClass("show-sidebar");

    });


    // Sublist Sidebar
    try {
      var arrow = $('.js-arrow');
      arrow.each(function () {
        var that = $(this);
        that.on('click', function (e) {
          e.preventDefault();
          that.find(".arrow").toggleClass("up");
          that.toggleClass("open");
          that.parent().find('.js-sub-list').slideToggle("250");
        });
      });

    } catch (error) {
      console.log(error);
    }


    try {
      // Hamburger Menu
      $('.hamburger').on('click', function () {
        $(this).toggleClass('is-active');
        $('.navbar-mobile').slideToggle('500');
      });
      $('.navbar-mobile__list li.has-dropdown > a').on('click', function () {
        var dropdown = $(this).siblings('ul.navbar-mobile__dropdown');
        $(this).toggleClass('active');
        $(dropdown).slideToggle('500');
        return false;
      });
    } catch (error) {
      console.log(error);
    }
  })(jQuery);
  (function ($) {
    // USE STRICT
    "use strict";

    // Load more
    try {
      var list_load = $('.js-list-load');
      if (list_load[0]) {
        list_load.each(function () {
          var that = $(this);
          that.find('.js-load-item').hide();
          var load_btn = that.find('.js-load-btn');
          load_btn.on('click', function (e) {
            $(this).text("Loading...").delay(1500).queue(function (next) {
              $(this).hide();
              that.find(".js-load-item").fadeToggle("slow", 'swing');
            });
            e.preventDefault();
          });
        })

      }
    } catch (error) {
      console.log(error);
    }

  })(jQuery);
  (function ($) {
    // USE STRICT
    "use strict";

    try {

      $('[data-toggle="tooltip"]').tooltip();

    } catch (error) {
      console.log(error);
    }

    // Chatbox
    try {
      var inbox_wrap = $('.js-inbox');
      var message = $('.au-message__item');
      message.each(function () {
        var that = $(this);

        that.on('click', function () {
          $(this).parent().parent().parent().toggleClass('show-chat-box');
        });
      });


    } catch (error) {
      console.log(error);
    }

  })(jQuery);
});