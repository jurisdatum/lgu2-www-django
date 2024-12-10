// legislation.gov.uk v2 js

// detect reducedMotion preference
	const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)')

// set default timeout intervals
	var animateInterval = 0
	var timeoutInterval = 0

	$(document).ready(function() {
		// show relevant skip links
		$('.legislation .legislation-skip').each(function() {
			$(this).css('display','')
		})
		$('.search .search-skip').each(function() {
			$(this).css('display','')
		})

	// make all content available to people who do not have CSS or JS enabled
		$('.initialise').each(function() {
			if($(this).attr('hidden')) {
				$(this).removeAttr('hidden')
			}
			else {
				$(this).attr('hidden',true)
			}
			$(this).removeClass('initialise')
		})

	// light/dark mode
		$('.mode button').on('click', function() {
			var theButtonId = $(this).attr('id')
			toggleMode(theButtonId)
		})
		if(localStorage.getItem('colour-scheme')) {
			var mode = localStorage.getItem('colour-scheme')
		}
		else {
			mode = 'system'			
		}
		toggleMode(mode)

	// header menu on mobile
		$('#open-menu').on('click', function() {
			if (reducedMotion && !reducedMotion.matches) {
				timeoutInterval = 360
			}
			$('#hdr-menu').css('display','block')
			setTimeout(function() { 
				$('#hdr-menu').css('left','0')
			},10)
			$('#hdr-menu').attr('role','dialog')
			$('#hdr-menu').attr('aria-label','Main menu')
			setTimeout(function() { 
				$('section').children().not('#hdr-menu').css('display','none')
				$('.section').children().not('#hdr-menu').css('display','none')
				$('#hdr-search').css('display','none')
				$('#hdr-search').css('height','')
				$('#close-menu').focus()
			},timeoutInterval)
		})

		$('#close-menu').on('click', function() {
			if (reducedMotion && !reducedMotion.matches) {
				timeoutInterval = 360
			}
			if($('#versions').css('left') == '0') {
				$('section').children().not('#hdr-menu').css('display','')
			}
			else {
				$('section').children().not('#hdr-menu').not('#versions').css('display','')	  
			}
			$('.section').children().not('#hdr-menu').css('display','')
			$('#hdr-search').css('display','')
			$('#open-menu').focus()
			$('#hdr-menu').removeAttr('role')
			$('#hdr-menu').removeAttr('aria-labelledby')
			$('#hdr-menu').css('left','')
			setTimeout(function() { 
				$('#hdr-menu').css('display','')
			},timeoutInterval)
		})

	// search on mobile
		$('#show-hide-search').on('click', function() {
			if (reducedMotion && !reducedMotion.matches) {
				timeoutInterval = 360
			}
			if($('#hdr-search').css('display') == 'block') {
				$('#hdr-search').css('height','')
				$('#hdr-search').attr('aria-label','')
				$('#show-hide-search').attr('aria-expanded',false)
				$('#show-hide-search').attr('aria-label','Show search')
				$('#show-hide-search').focus()
				setTimeout(function() { 
					$('#hdr-search').css('display','')
				},timeoutInterval)
			}
			else {
				$('#hdr-search').css('display','block')
				setTimeout(function() { 
					$('#hdr-search').css('height','4.5em')
				},10)
				$('#hdr-search').attr('aria-label','Search legislation')
				$('#show-hide-search').attr('aria-expanded',true)
				$('#show-hide-search').attr('aria-label','Hide search')
				$('#search').focus()
			}
		})

	// search filters on mobile
		$('#open-filters').on('click', function() {
			if (reducedMotion && !reducedMotion.matches) {
				timeoutInterval = 360
			}
			$('#filters-menu').css('display','block')
			setTimeout(function() { 
				$('#filters-menu').css('left','0')
			},10)
			$('#filters-menu').attr('role','dialog')
			$('#filters-menu').attr('aria-label','Filter your results')
			setTimeout(function() { 
				$('section').children().not('#filters-menu, #search-metadata').css('display','none')
				$('.section').children().not('#filters-menu, #search-metadata').css('display','none')
				$('h1').css('display','none')
				$('#hdr-menu').css('display','none')
				$('#hdr-search').css('display','none')
				$('#hdr-search').css('height','')
				$('#close-filters').focus()
			},timeoutInterval)
		})

		$('#close-filters').on('click', function() {
			if (reducedMotion && !reducedMotion.matches) {
				timeoutInterval = 360
			}
			$('h1').css('display','')
			$('section').children().not('#filters-menu, #search-metadata').css('display','')
			$('.section').children().not('#filters-menu, #search-metadata').css('display','')
			$('#hdr-search').css('display','')
			$('#open-filters').focus()
			$('#filters-menu').removeAttr('role')
			$('#filters-menu').removeAttr('aria-labelledby')
			$('#filters-menu').css('left','')
			setTimeout(function() { 
				$('#filters-menu').css('display','')
			},timeoutInterval)
		})

	// if there is a timeline
		if($('section#timeline').length != 0) {

		// point-in-time and timeline controls
			$('#pit-btn').on('click', function() {
			if (reducedMotion && !reducedMotion.matches) {
				timeoutInterval = 750
			}
				var elementId = 'pit-search'
				var toggle = 'pit-btn'
				if($('#' + elementId).hasClass('pit-open'))
				{
					$('#' + elementId).css('max-height','')
					$('#' + toggle).removeClass('toggle-open')
					$('#' + elementId).removeClass('pit-open')
					$('#' + toggle).attr('aria-expanded',false)
					setTimeout(function(){
						$('#' + elementId).attr('hidden',true)
					},timeoutInterval)
				}
				else
				{
					$('#' + elementId).css('max-height','unset')
					var maxHeight = $('#' + elementId).height();
					$('#' + elementId).css('max-height','')
					$('#' + toggle).addClass('toggle-open')
					$('#' + elementId).removeAttr('hidden')
					$('#' + toggle).attr('aria-expanded',true)
					setTimeout(function(){
						$('#' + elementId).css('max-height',maxHeight)
						$('#' + elementId).addClass('pit-open')
					},1)
				}
			})

			$('#open-versions').on('click', function() {
				openTimeline()
			})

			$('#close-versions').on('click', function() {
				if (reducedMotion && !reducedMotion.matches) {
					timeoutInterval = 360
				}
				$('section').children().not('#versions').not('#versions').css('display','')		  
				$('.section').children().not('#versions').css('display','')
				$('#hdr-search').css('display','')
				$('#open-versions').focus()
				$('#versions').css('left','')
				setTimeout(function() { 
					$('#versions').css('display','')
				},timeoutInterval)
			})

		// selecting a version from the timeline
			$('.versions li a').on('click', function() {
				$('.versions').removeClass('current-point-in-time')
				$('.versions').removeClass('original-point-in-time')
				$('.versions li.point-in-time .point-in-time').remove()
				$('.versions li.point-in-time').removeClass('point-in-time')
				loadVersion(this)
			})

		// timeline scrollbar controls
			var down = false

			$('#timeline ul').scroll(function() {
				var scrollbarwidth = $('.scrollbar').width()
				var liwidth = $('#timeline ul').children('li:not(.original, .break):first').width()
				var noOfBreaks = ($('#timeline ul').children('li:not(.original, .current).break').length)
				var addForBreak = $('#timeline ul').children('li:not(.original, .current).break').width() - liwidth
				var noOfPiTs = ($('#timeline ul').children('li:not(.original, .current).point-in-time').length)
				var addForPiT = $('#timeline ul').children('li:not(.original, .current).point-in-time').outerWidth() - liwidth
				var ulwidth = ($('#timeline ul').children('li').length - 2) * liwidth - scrollbarwidth + (addForBreak * noOfBreaks) + (addForPiT * noOfPiTs)
				var scrollx = $('#timeline ul').scrollLeft()
				var dragwidth = $('.drag').width()
				var dragstripwidth = $('.drag-strip').width()
				var thefactor = ((dragstripwidth - dragwidth) / ulwidth)

				if(!down) {
					$('.drag').css('left',scrollx * thefactor)
				}

				if(scrollx >= ulwidth) {
					$('.right').attr('disabled','disabled')
				}
				else {
					$('.right').removeAttr('disabled')
				}

				if(scrollx == 0) {
					$('.left').attr('disabled','disabled')
				}
				else {
					$('.left').removeAttr('disabled')
				}
			})

			$('.right').on('click', function() {
				var scrolltx = $('#timeline ul').scrollLeft()
				var liwidth = $('#timeline ul').children('li:not(.original, .break):first').width()
				var scrollbarwidth = $('.scrollbar').width()

				if (reducedMotion && !reducedMotion.matches) {
					animateInterval = 400
				}
				$('#timeline ul').animate({scrollLeft: scrolltx + scrollbarwidth - liwidth}, animateInterval)
			})

			$('.left').on('click', function() {
				var scrolltx = $('#timeline ul').scrollLeft()
				var liwidth = $('#timeline ul').children('li:not(.original, .break):first').width()
				var scrollbarwidth = $('.scrollbar').width()

				if (reducedMotion && !reducedMotion.matches) {
					animateInterval = 400
				}
				$('#timeline ul').animate({scrollLeft: scrolltx - scrollbarwidth + liwidth}, animateInterval)
			})

			$(function() {
				$('.drag').draggable({containment: '.drag-strip'})
			})

			$('.drag').on('drag', function() {
				down = true
				var scrollbarwidth = $('.scrollbar').width()
				var liwidth = $('#timeline ul').children('li:not(.original, .break):first').width()
				var noOfBreaks = ($('#timeline ul').children('li:not(.original, .current).break').length)
				var addForBreak = $('#timeline ul').children('li:not(.original, .current).break').width() - liwidth
				var noOfPiTs = ($('#timeline ul').children('li:not(.original, .current).point-in-time').length)
				var addForPiT = $('#timeline ul').children('li:not(.original, .current).point-in-time').outerWidth() - liwidth
				var ulwidth = ($('#timeline ul').children('li').length - 2) * liwidth - scrollbarwidth + (addForBreak * noOfBreaks) + (addForPiT * noOfPiTs)

				var dragwidth = $('.drag').width()
				var dragleft = $('.drag').css('left')
				dragleft = parseInt(dragleft.replace(/^\.|[^-?\d\.]|\.(?=.*\.)|^0+(?=\d)/g, ''))
				var dragstripwidth = $('.drag-strip').width()
				var thefactor = ((dragstripwidth - dragwidth) / ulwidth)

				$('#timeline ul').scrollLeft(dragleft / thefactor)
			})
			$('.drag').on('dragstop', function() {
				down = false
			})

		// timeline contextual help
			$('.contextual-help button').on('click', function() {
				if (reducedMotion && !reducedMotion.matches) {
					timeoutInterval = 250
				}
				var elementId = this.closest('.contextual-help').id
				if($('#' + elementId + ' div').attr('hidden')) {
					var maxHeight = 0
					$('#' + elementId + ' button').attr('aria-expanded',true)
					$('#' + elementId + ' div').removeAttr('hidden')
					$('#' + elementId + ' div button').removeAttr('hidden')
					$('#' + elementId + ' div div').removeAttr('hidden')
					$('#' + elementId + ' div').css('max-height','unset')
					if($(window).width() > 1023) {
						maxHeight = $('#' + elementId + ' div').height() - 10;
						$('#' + elementId + ' div button').css('display','block')
					}
					else {
						maxHeight = $('#' + elementId).height();
					}
					$('#' + elementId + ' div').css('max-height','')
					$('#' + elementId).addClass('accordion-open')
					setTimeout(function() {
						$('#' + elementId + ' div').css('max-height',maxHeight)
					},1)
				}
				else {
					$('#' + elementId + ' div').css('max-height','')
					setTimeout(function() {
						$('#' + elementId + ' div button').css('display','none')
						$('#' + elementId + ' div button').attr('hidden',true)
						$('#' + elementId + ' div div').attr('hidden',true)
						$('#' + elementId + ' button').attr('aria-expanded',false)
						$('#' + elementId + ' div').attr('hidden',true)
						$('#' + elementId).removeClass('accordion-open')
					},timeoutInterval)
				}
			})

		// open timeline if point-in-time or historical verion is selected 
			if($(window).width() > 1023 && (!$('.current').is('[aria-current]') || $('.current').is('.point-in-time') || $('.current').is('.prospective')))
			{
				setTimeout(function() { 
					openTimeline()
				},150)
			}
		}

	// if there is legislation text
		if($('section#legislation-text').length != 0) {
		// set up markers
			$('.legislation-text li:not(.legislation-footnotes li)').each(function() {
				if(!$(this).attr('data-level') && $(this).parent().prop('tagName').toLowerCase() == 'ol'){
					if($(this).children('.prefix').length == 0){
						$(this).prepend($('<span class="prefix"></span>'))
					}
					if($(this).children(':header').eq(0).children('.prefix').length == 0){
						$(this).children(':header').eq(0).prepend($('<span class="prefix"></span>'))
					}
					if($(this).attr('value')) {
						var index = $(this).attr('value')
					}
					else if($(this).index() === 0)
						index = 1
					else
					{
						index = parseFloat($(this).prev().attr('value')) + 1
					}

					$(this).attr('value',index)

					if($(this).parent().attr('type') == 'a') {
						index = String.fromCharCode(64 + parseInt(index)).toLowerCase()
					}
					else if($(this).parent().attr('type') == 'i') {
						index = romanize(index).toLowerCase()
					}

					if($(this).parent().parent().prop('tagName').toLowerCase() == 'section') {
						$(this).children(':header').eq(0).children('.prefix').append($('<span aria-hidden="true" class="marker">' + index + ' </span>'))
					}
					else {
						$(this).children('.prefix').append($('<span aria-hidden="true" class="marker">(' + index + ') </span>'))
					}
				}
			})
			$('head').append('<style type="text/css">ol > li:not(.legislation-footnotes li)::marker {color: rgba(30,30,30,0)}</style>')

		// if there are status panels
			if($('.status-panel').length != 0) {
				setTimeout(function() { 
				$('#legislation-text .status-panel').each(function() {
					var statusPanelType = $(this).attr('paneltype')
						setStatusPin(statusPanelType)
				})
				},100)
				setTimeout(function() { 
					scrollStatusPanels()
				},100)

			// status panel controls
				$('.status-panel .pin').on('click', function() {
					var theStatusPanelType = $(this).closest('.status-panel').attr('paneltype')
					toggleStatusPin(theStatusPanelType)
				})

				$('.status-panel .hdrCtrl').on('click', function() {
				//operate all at once
					/* var theStatusPanelType = $(this).closest('.status-panel').attr('paneltype')
					$('.status-panel[paneltype="' + theStatusPanelType + '"]').each(function() {
						var theStatusPanelId = $(this).attr('id')
						showHideStatusPanel(theStatusPanelId)
					}); */
				//operate individually
					var theStatusPanelId = $(this).closest('.status-panel').attr('id')
					showHideStatusPanel(theStatusPanelId)
				})
				
				$('#legislation-metadata .up-to-date.not-up-to-date #notUpToDateAlt').on('click', function() {
					$('.status-panel[paneltype="notUpToDate"]').each(function() {
						var theStatusPanelId = $(this).attr('id')
						showHideStatusPanel(theStatusPanelId)
					});
				})
				$('#legislation-metadata .in-force.not-up-to-date #commencementAlt').on('click', function() {
					$('.status-panel[paneltype="notUpToDate"]').each(function() {
						var theStatusPanelId = $(this).attr('id')
						showHideStatusPanel(theStatusPanelId)
					});
				})
				$('#legislation-metadata .in-force:not(.not-up-to-date) #commencementAlt').on('click', function() {
					$('.status-panel[paneltype="commencement"]').each(function() {
						var theStatusPanelId = $(this).attr('id')
						showHideStatusPanel(theStatusPanelId)
					});
				})
				$('#legislation-metadata .geographical-extent.not-up-to-date #geogExtentAlt').on('click', function() {
					$('.status-panel[paneltype="notUpToDate"]').each(function() {
						var theStatusPanelId = $(this).attr('id')
						showHideStatusPanel(theStatusPanelId)
					});
				})
				$('#legislation-metadata .geographical-extent:not(.not-up-to-date) #geogExtentAlt').on('click', function() {
					$('.status-panel[paneltype="geogExtent"]').each(function() {
						var theStatusPanelId = $(this).attr('id')
						showHideStatusPanel(theStatusPanelId)
					});
				})
			}

		// show/hide annotations
			$('.annotation-start button:not(.annotation-detail button)').on('click', function() {
				var elementId = this.id.slice(0,-5)
				annotations(elementId)
			})

			$('.annotation-detail button').on('click', function() {
				var elementId = this.closest('.annotation-detail').id
				annotations(elementId)
			})
		}

	// if there are metadata panels
		if($('#legislation-metadata').length != 0) {
			$('#key-versions button').on('click', function() {
				metadataPanel("#key-versions")
			})
			$('#other-formats button').on('click', function() {
				metadataPanel("#other-formats")
			})


		}

	// escape key functions
		$(document).keydown(function(e) {
			if(e.keyCode == 27) {
				if (reducedMotion && !reducedMotion.matches) {
					timeoutInterval = 360
				}
				if($('#hdr-menu').css('display') == 'block') {
					if($('#versions').css('left') == '0') {
						$('section').children().not('#hdr-menu').css('display','')
					}
					else {
						$('section').children().not('#hdr-menu').not('#versions').css('display','')
					}
					$('.section').children().not('#hdr-menu').css('display','')
					$('#hdr-search').css('display','')
					$('#open-menu').focus()
					$('#hdr-menu').removeAttr('role')
					$('#hdr-menu').removeAttr('aria-labelledby')
					$('#hdr-menu').css('left','')
					setTimeout(function() { 
						$('#hdr-menu').css('display','')
					},timeoutInterval)
				}
				else if($('#hdr-search').css('display') == 'block') {
					$('#hdr-search').css('height','')
					$('#hdr-search').attr('aria-label','')
					$('#show-hide-search').attr('aria-expanded',false)
					$('#show-hide-search').attr('aria-label','Show search')
					$('#show-hide-search').focus()
					setTimeout(function() { 
						$('#hdr-search').css('display','')
					},timeoutInterval)
				}
				else if($('#versions').css('display') == 'block') {
					$('section').children().not('#versions').not('#versions').css('display','')
					$('.section').children().not('#versions').css('display','')
					$('#hdr-search').css('display','')
					$('#open-versions').focus()
					$('#versions').css('left','')
					setTimeout(function() { 
						$('#versions').css('display','')
					},timeoutInterval)
				}
				else if($('#filters-menu').css('display') == 'block') {
					$('h1').css('display','')
					$('section').children().not('#filters-menu, #search-metadata').css('display','')
					$('.section').children().not('#filters-menu, #search-metadata').css('display','')
					$('#hdr-search').css('display','')
					$('#open-filters').focus()
					$('#filters-menu').removeAttr('role')
					$('#filters-menu').removeAttr('aria-labelledby')
					$('#filters-menu').css('left','')
					setTimeout(function() { 
						$('#filters-menu').css('display','')
					},timeoutInterval)
				}
				if($('section#legislation-text').length != 0) {
					$('.annotation-start button:not(.annotation-detail button)').each(function() {
						var elementId = this.id.slice(0,-5)
						hideAnnotations(elementId)
					})
				}
			}
		})

	// on window resize
		$(window).resize(function() {
			if($(window).width() > 767) {
				if (reducedMotion && !reducedMotion.matches) {
					timeoutInterval = 360
				}

				if($('#versions').css('left') == '0') {
					$('section').children().not('#hdr-menu').css('display','')
				}
				else {
					$('section').children().not('#hdr-menu').not('#versions').css('display','')
				}

				$('.section').children().not('#hdr-menu').css('display','')
				$('#hdr-search').css('display','')
					$('#open-menu').focus()
					$('#hdr-menu').removeAttr('role')
					$('#hdr-menu').removeAttr('aria-labelledby')
				$('#hdr-menu').css('left','')

				setTimeout(function() { 
					$('#hdr-menu').css('display','')
				},timeoutInterval)

				$('#hdr-search').css('height','')
				$('#hdr-search').attr('aria-label','')
				$('#show-hide-search').attr('aria-expanded',false)
				$('#show-hide-search').attr('aria-label','Show search')
				$('#show-hide-search').focus()

				setTimeout(function() { 
					$('#hdr-search').css('display','')
				},timeoutInterval)
			}
			if($(window).width() < 1024 && $('#hdr-menu').css('display') == 'block') {
				if($('section#timeline').length != 0) {
					$('#versions').css('display','none')
					$('#timeline').css('height','')
					$('#legislation-metadata').removeClass('metadata-open-timeline')
					$('#open-versions').removeClass('open-timeline')
					$('#timeline').removeClass('scrollable-timeline')
				}
			}
			setTimeout(function() { 
				assignStatusPanelIds()
			},100)
		})

	// on scroll
		$(window).scroll(function() {
			if($('.status-panel.pinned').length != 0) {
				scrollStatusPanels()
			}
		})
	})

	function toggleMode(mode) {
		if(mode == 'system' || mode == '') {
			$('.mode button').removeClass('selected')
			$('#system').addClass('selected')
			const userPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
			if(userPrefersDark) {
				document.documentElement.setAttribute('colour-scheme', 'dark')
				localStorage.removeItem('colour-scheme')
			}
			else {
				document.documentElement.setAttribute('colour-scheme', 'light')
				localStorage.removeItem('colour-scheme')
			}
			window.matchMedia('(prefers-color-scheme: dark)').addListener(({ matches }) =>
			{
				if((mode == 'system' || mode == '') && matches) {
				document.documentElement.setAttribute('colour-scheme', 'dark')
				localStorage.removeItem('colour-scheme')
				} else if(mode == 'system' || mode == '') {
				document.documentElement.setAttribute('colour-scheme', 'light')
				localStorage.removeItem('colour-scheme')
				}
			})
		}
		else {
			document.documentElement.setAttribute('colour-scheme', mode)
			localStorage.setItem('colour-scheme', mode)
			$('.mode button').removeClass('selected')
			$('#' + mode).addClass('selected')
		}
	}

	function metadataPanel(panel) {
		if (reducedMotion && !reducedMotion.matches) {
			timeoutInterval = 250
		}
		if($(panel + ' div').attr('hidden')) {
			$(panel + ' div').css('max-height','unset')
			var maxHeight = $(panel + ' div').height() + 40;
			$(panel + ' div').css('max-height','')
			$(panel + ' button').attr('aria-expanded',true)
			$(panel + ' div').removeAttr('hidden')
			$(panel).addClass('accordion-open')
			setTimeout(function() {
				$(panel + ' div').css('max-height',maxHeight)
			},1)
		}
		else {
			$(panel + ' div').css('max-height','')
			$(panel).removeClass('accordion-open')
			setTimeout(function() {
				$(panel + ' button').attr('aria-expanded',false)
				$(panel + ' div').attr('hidden',true)
			},timeoutInterval)
		}
	}

	function openTimeline() {
		if($(window).width() < 1024) {
			if (reducedMotion && !reducedMotion.matches) {
				timeoutInterval = 360
			}
			$('#versions').css('display','block')
			setTimeout(function() { 
				$('#versions').css('left','0')
			},10)
			setTimeout(function() { 
				$('section').children().not('#versions').css('display','none')
				$('.section').children().not('#versions').css('display','none')
				$('#hdr-search').css('display','none')
				$('#hdr-search').css('height','')
				$('#close-versions').focus()
			},timeoutInterval)
		}
		else if($('#versions').css('display') == 'block') {
			$('#versions').css('display','none')
			$('#timeline').css('height','')
			$('#legislation-metadata').removeClass('metadata-open-timeline')
			$('#open-versions').removeClass('open-timeline')
			$('#timeline').removeClass('scrollable-timeline')
			$('#timeline').removeClass('scrollable-timeline')
		}
		else {
			$('#versions').css('display','block')
			$('#timeline').css('height','auto')
			$('#legislation-metadata').addClass('metadata-open-timeline')
			$('#open-versions').addClass('open-timeline')

			var ulwidth = $('#timeline ul').children('li').length
			var liOriginal = $('#timeline ul').children('li.original').width()
			var liCurrent = $('#timeline ul').children('li.current').width()
			var addForExtremeties = liOriginal + liCurrent
			var timelineScrollWidth = $('#timeline ul').get(0).scrollWidth
			var timelineWidth = $('#timeline').width()
			if((timelineScrollWidth + addForExtremeties) > timelineWidth && ulwidth > 1)
			{
				$('#timeline').addClass('scrollable-timeline')
			}
			else
			{
				$('#timeline').removeClass('scrollable-timeline')
			}
			if(ulwidth < 3 && $('#timeline li:last-child').attr('aria-current')) {
				$('.versions').addClass('selected')
			}
			else
			{
				$('.versions').removeClass('selected')
			}

		}
		$('.versions li').each(function() {
			var attr = $(this).attr('aria-current')
			if (typeof attr !== 'undefined' && attr !== false){

				loadVersion($(this).children('a'),'noanim','initialise')
			}
		})
	}

	function loadVersion(version,anim,initialise) {
		animateInterval = 0
		version = $(version).parent()

		$('.versions li').each(function() {
			$(this).removeAttr('aria-current')
			$('.versions li a .prefix').remove()

		})
		$(version).attr('aria-current','page')
		$(version).find('.version').prepend($('<span class="prefix">You are viewing </span>'))

		if($(window).width() < 1023 && initialise != 'initialise') {
			setTimeout(function() { 
				if (reducedMotion && !reducedMotion.matches) {
					timeoutInterval = 360
				}
				$('section').children().not('#versions').not('#versions').css('display','');	  
				$('.section').children().not('#versions').css('display','')
				$('#hdr-search').css('display','')
				$('#open-versions').focus()
				$('#versions').css('left','')
				setTimeout(function() { 
					$('#versions').css('display','')
					if (reducedMotion && !reducedMotion.matches) {
						timeoutInterval = 500
					}
				},timeoutInterval)
			},timeoutInterval)
		}

		if($('#timeline li:last-child').attr('aria-current')) {
			$('.versions').addClass('selected')
		}
		else
		{
			$('.versions').removeClass('selected')
		}

		var liwidth = $('#timeline ul').children('li:not(.original, .break):first').width()
		var noOfBreaks = ($('#timeline ul').children('li:not(.original, .current).break').length)
		var addForBreak = $('#timeline ul').children('li:not(.original, .current).break').width() - liwidth
		var noOfPiTs = ($('#timeline ul').children('li:not(.original, .current).point-in-time').length)
		var addForPiT = $('#timeline ul').children('li:not(.original, .current).point-in-time').outerWidth() - liwidth
		var index = $(version).index()
		var scrollbarwidth = $('.scrollbar').width()

		if (reducedMotion && !reducedMotion.matches && anim != 'noanim') {
			animateInterval = 400
		}
		$('#timeline ul').animate({scrollLeft: ((index * liwidth) + (addForBreak * noOfBreaks) + (addForPiT * noOfPiTs) + (liwidth / 2) - (scrollbarwidth * 0.7))}, animateInterval)
	}

	function romanize(num) {
		if (isNaN(num))
			return NaN
		var digits = String(+num).split(''),
			key = ['','C','CC','CCC','CD','D','DC','DCC','DCCC','CM',
					'','X','XX','XXX','XL','L','LX','LXX','LXXX','XC',
					'','I','II','III','IV','V','VI','VII','VIII','IX'],
			roman = '',
			i = 3
		while (i--)
			roman = (key[+digits.pop() + (i * 10)] || '') + roman
		return Array(+digits.join('') + 1).join('M') + roman
	}

	function assignStatusPanelIds() {
		var statusPanelsIndex = 1
		$('#legislation-text .status-panels').each(function() {
			$(this).attr('statusPanelsId','')
			if(!$(this).hasClass('notUpToDate')) {
				$(this).css('z-index','')
			}
			statusPanelsIndex += 1
			$(this).attr('statusPanelsId',statusPanelsIndex)
			if(!$(this).hasClass('notUpToDate')) {
				$(this).css('z-index',(statusPanelsIndex * 10))
			}
			var pinnedStatusPanelIndex = 0
			var statusPanelHeight = 0
			$(this).children('.status-panel').each(function() {
				$(this).attr('paddingRequired',statusPanelHeight)
				$(this).attr('pinnedStatusPanelId','')
				$(this).removeClass('first-pinned')
				if($(this).hasClass('pinned')){
					pinnedStatusPanelIndex += 1
					$(this).attr('pinnedStatusPanelId',pinnedStatusPanelIndex)
					statusPanelHeight += $(this).outerHeight()

					if($(this).attr('pinnedStatusPanelId') == '1') {
						$(this).addClass('first-pinned')
					}
				}
			})

			$(this).children('.status-panel').each(function() {
				$(this).removeClass('last-pinned')
				if($(this).hasClass('pinned')){
					var thePinnedStatusPanelNumber = parseInt($(this).attr('pinnedStatusPanelId')) +1
					var theParent = $(this).closest('.status-panels').attr('statuspanelsid')
					if($('.status-panels[statuspanelsid=' + theParent + ']' + ' .status-panel[pinnedStatusPanelId=' + parseInt(thePinnedStatusPanelNumber) + ']').length == 0) {
						$(this).addClass('last-pinned')
						if(!$(this).parent().hasClass('notUpToDate')){
							$('.status-panels.notUpToDate .last-pinned').removeClass('last-pinned')
						}
					}
				}
				else {
					$(this).css('display','')
				}
			})
		})
		$(window).scrollTop($(window).scrollTop()+1);
		$(window).scrollTop($(window).scrollTop()-1);
	}

	function getStatusPin(statusPanelType) {
		if(localStorage.getItem(statusPanelType)) {
			var statusPin = localStorage.getItem(statusPanelType)
		}
		return statusPin
	}

	function setStatusPin(statusPanelType) {
		var statusPin = getStatusPin(statusPanelType)
		$('.status-panel[paneltype="' + statusPanelType + '"]').each(function() {
			var statusPanel = $(this).attr('id')
			if(statusPin != 'pinned') {
				$('#' + statusPanel + ' .pin').text('Pin this panel')
			}
			else {
				$('#' + statusPanel).addClass('pinned')
				$('#' + statusPanel + ' .pin').text('Unpin this panel')
			}
		})
		setTimeout(function() { 
			assignStatusPanelIds()
		},100)
	}

	function toggleStatusPin(statusPanelType) {
		var statusType = getStatusPin(statusPanelType)
		if(statusType != 'pinned') {
			$('.status-panel[paneltype="' + statusPanelType + '"]').each(function() {
				var statusPanel = $(this).attr('id')
				$('#' + statusPanel).addClass('pinned')
				$('#' + statusPanel + ' .pin').text('Unpin this panel')
				$(window).scrollTop($(window).scrollTop()+1);
				$(window).scrollTop($(window).scrollTop()-1);
				localStorage.setItem(statusPanelType, 'pinned')
			})
		}
		else {
			$('.status-panel[paneltype="' + statusPanelType + '"]').each(function() {
				var statusPanel = $(this).attr('id')
				$('#' + statusPanel).removeClass('pinned')				
				$('#' + statusPanel).removeClass('scrolled')				
				$('#' + statusPanel).css('margin-top','')				
				$('#' + statusPanel).prev().css('height','')
				$('#' + statusPanel + ' .pin').text('Pin this panel')
				$(window).scrollTop($(window).scrollTop()+1);
				$(window).scrollTop($(window).scrollTop()-1);
				localStorage.removeItem(statusPanelType)
			})
		}
		assignStatusPanelIds()
	}

	function scrollStatusPanels() {
		$('#legislation-text .status-panels').each(function() {
			var theStatusPanels = $(this).attr("statusPanelsId")
			var theNextStatusPanels = parseInt(theStatusPanels) + 1

			if($('#notUpToDateStatus').length == 0) {
				var theNotUpToDateStatusPanelHeight = 0
			}
			else {
				if($(this).parent().hasClass('notUpToDate')) {
					theNotUpToDateStatusPanelHeight = 0				
				}
				else if($('.pinned.notUpToDate').length == 0) {
					theNotUpToDateStatusPanelHeight = 0
				}
				else {
					theNotUpToDateStatusPanelHeight = parseInt($('.pinned.notUpToDate').outerHeight() + 16)
				}
			}
			
			if($(this).nextAll('[statusPanelsId="'+ theNextStatusPanels +'"]').length != 0) {
				if(($(window).scrollTop() + theNotUpToDateStatusPanelHeight) > $(this).nextAll('[statusPanelsId="'+ theNextStatusPanels +'"]').offset().top) {
					setTimeout(function() {
						$('[statusPanelsId="' + theStatusPanels + '"]').children('.pinned:not(.notUpToDate)').css('display','none')
					},10)
				}
				else {
					setTimeout(function() {
						$('[statusPanelsId="' + theStatusPanels + '"]').children('.pinned:not(.notUpToDate)').css('display','')
					},10)
				}
			}
		})

		$('#legislation-text [id^="scrollStart-"]').each(function() {
			var theStatusPanel = $(this).next().attr('id')
			var theStatusPanelsId = $(this).attr("statusPanelsId")
			var thePinnedStatusPanel = $('#' + theStatusPanel + '.pinned')
			var theStatusPanelNumber = parseInt($('#' + theStatusPanel).attr('pinnedStatusPanelId'))
			var theStatusPanelPadding = parseInt($('#' + theStatusPanel).attr("paddingRequired"))
			var theStatusPanelHeight = parseInt($('#' + theStatusPanel).outerHeight())
			if($('#notUpToDateStatus').length == 0) {
				var theNotUpToDateStatusPanelHeight = 0
			}
			else {
				if($(this).parent().hasClass('notUpToDate')) {
					theNotUpToDateStatusPanelHeight = 0				
				}
				else if($('.pinned.notUpToDate').length == 0) {
					theNotUpToDateStatusPanelHeight = 0
				}
				else {
					theNotUpToDateStatusPanelHeight = parseInt($('.pinned.notUpToDate').outerHeight())
				}
			}
			var thePinnedScollStart = $('#' + theStatusPanel + '.pinned').prev()
			var prePadding = 16 * (theStatusPanelNumber -1)
			var postPadding = 16
			if($(this).next().hasClass('first-pinned') && theNotUpToDateStatusPanelHeight == 0) {
				prePadding = 0
			}
			else if($(this).next().hasClass('first-pinned')) {
				prePadding = 16
			}

			if($(window).scrollTop() >= ($(this).offset().top - theStatusPanelPadding - prePadding - theNotUpToDateStatusPanelHeight)) {
				setTimeout(function() {
					thePinnedStatusPanel.removeClass('scrolling')
					thePinnedStatusPanel.addClass('scrolled')
					if(!$(thePinnedStatusPanel).hasClass('notUpToDate')) {
						thePinnedStatusPanel.css('margin-top',theStatusPanelPadding + prePadding + theNotUpToDateStatusPanelHeight)
					}
					if($(this).next().hasClass('first-pinned')) {
						thePinnedScollStart.css('height',theStatusPanelHeight + postPadding)
					}
					else if($(this).next().hasClass('last-pinned')) {
						thePinnedScollStart.css('height',theStatusPanelPadding + postPadding)
					}
					else {
						thePinnedScollStart.css('height',theStatusPanelHeight + postPadding)
					}
				},10)
			}
			else if(($(window).scrollTop() > ($(this).offset().top - theStatusPanelPadding - prePadding - theNotUpToDateStatusPanelHeight - theStatusPanelHeight)) && $(window).scrollTop() < ($(this).offset().top - theStatusPanelPadding - prePadding - theNotUpToDateStatusPanelHeight)) {
				setTimeout(function() {
					thePinnedScollStart.css('height','')
					thePinnedStatusPanel.css('margin-top','')
					thePinnedStatusPanel.removeClass('scrolled')
					if ($(thePinnedStatusPanel).hasClass('commencement')) {
						thePinnedStatusPanel.addClass('scrolling')
					}
				},10)
			}
			else {
				setTimeout(function() { 
					thePinnedScollStart.css('height','')
					thePinnedStatusPanel.css('margin-top','')
					thePinnedStatusPanel.removeClass('scrolled')
					if ($(thePinnedStatusPanel).hasClass('commencement')) {
						thePinnedStatusPanel.removeClass('scrolling')
					}
				},10)
			}
		})
	}

	function showHideStatusPanel(statusPanel) {
		timeoutInterval = 1
		var originalText = $('#' + statusPanel + 'Hdr').attr('originalText')
		var openedText = $('#' + statusPanel + 'Hdr').attr('openedText')
		var theStatusPanelType = $('#' + statusPanel).attr('paneltype')
		
		if(typeof originalText === 'undefined') {
			originalText = $('#' + statusPanel + 'Hdr').text()
			$('#' + statusPanel + 'Hdr').attr('originalText',originalText)
		}
		if(typeof openedText === 'undefined') {
			if(theStatusPanelType == "notUpToDate") {
				openedText = "Hide detail of these changes"
			}
			else if(theStatusPanelType == "commencement") {
				openedText = "Hide in force information"
			}
			else {
				openedText = "Hide " + originalText.substr(originalText.indexOf(" ") + 1);
			}
		}
		
		if($('#' + statusPanel + ' .status-detail').attr('hidden')) {
			$('#' + statusPanel + ' .status-detail').removeAttr('hidden')
			$('#' + statusPanel + 'Hdr').attr('aria-expanded',true)
			$('#' + statusPanel + 'Alt').attr('aria-expanded',true)
			$('#' + statusPanel + 'Hdr').text(openedText)
			if($('#notUpToDate').length == 0 || ($('#notUpToDate').length != 0 && statusPanel == "notUpToDate")) {
				$('#' + statusPanel + 'Alt').text(openedText)
			}
			setTimeout(function() {
				$('#' + statusPanel).addClass('accordion-open')
				setTimeout(function() {
					var messagingheight = $('#' + statusPanel + ' .affecting-legislation').height()
					var detailMaxheight = $('#' + statusPanel + ' .status-detail').height()
					if(messagingheight > detailMaxheight) {
						$('#' + statusPanel).addClass('scrollable-messaging')
					}
				},timeoutInterval)
			},timeoutInterval)
		}
		else {
			$('#' + statusPanel).removeClass('accordion-open')
			if (reducedMotion && !reducedMotion.matches) {
				timeoutInterval = 250
			}
			setTimeout(function() {
				if($('#notUpToDate').length == 0 || ($('#notUpToDate').length != 0 && theStatusPanelType == "notUpToDate")) {
					$('#' + statusPanel + 'Alt').text(originalText)
				}
				$('#' + statusPanel + 'Hdr').text(originalText)
				$('#' + statusPanel + 'Hdr').attr('aria-expanded',false)
				$('#' + statusPanel + 'Alt').attr('aria-expanded',false)
				$('#' + statusPanel + ' .status-detail').attr('hidden',true)
				$('#' + statusPanel).removeClass('scrollable-messaging')
			},timeoutInterval)
		}

		if (reducedMotion && !reducedMotion.matches) {
			timeoutInterval = 500
		}
		setTimeout(function() {
			assignStatusPanelIds()
		},timeoutInterval)
	}

	function annotations(elementId) {
		if($('#' + elementId).attr('hidden')) {
			$('#' + elementId + '-open').attr('aria-expanded',true)
			$('#' + elementId).removeAttr('hidden')
			$('#' + elementId + ' button').removeAttr('hidden')
			$('#' + elementId + ' button').attr('aria-expanded',true)
			$('#' + elementId).addClass('annotation-open')

			var elementHeight = $('#' + elementId).outerHeight() + 28
			var buttonWidth = $('#' + elementId + '-open').outerWidth() + 7

			$('#' + elementId).css('margin-top','-' + elementHeight + 'px')

			if($(window).width() > 767) {
				$('.prefix #' + elementId).css('margin-left','-' + buttonWidth + 'px')
				$('.prefix .wrapper #' + elementId).css('margin-left','-10px')
			}
			else {
				$('.prefix #' + elementId).css('margin-left','-' + (buttonWidth - 1) + 'px')
				$('.extended-annotations .prefix #' + elementId).css('margin-left','-' + (buttonWidth - 7) + 'px')
				$('.prefix .wrapper #' + elementId).css('margin-left','-' + (buttonWidth - 49) + 'px')
				$('.prefix .wrapper #' + elementId).css('margin-top','-' + (elementHeight + 4) + 'px')
			}

			var a = $('#' + elementId).offset().left
			var b = $('#legislation-metadata').offset().left
			var annotationRight = a + $('#' + elementId).width()
			var legTextRight = b + $('#legislation-metadata').width()

			$('#' + elementId + '-open').addClass('button-open')					

			if((annotationRight + 30) > legTextRight) {
				$('#' + elementId).css('margin-left', (legTextRight - annotationRight - 34) + 'px')
			}
		}
		else {
			hideAnnotations(elementId)
		}
	}

	function hideAnnotations(elementId) {
		$('#' + elementId).css('max-height','')
		$('#' + elementId + '-open').attr('aria-expanded',false)
		$('#' + elementId).attr('hidden',true)
		$('#' + elementId + ' button').attr('hidden',true)
		$('#' + elementId + ' button').attr('aria-expanded',false)
		$('#' + elementId).removeClass('annotation-open')
		$('#' + elementId).css('margin-top','')
		$('#' + elementId).css('margin-left', '')
		$('#' + elementId + '-open').removeClass('button-open')					
	}
