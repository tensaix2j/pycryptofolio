

function SimpleList() {

	//---------------
	this.get_exchange_rates = function() {

		var sl = this;
	    
		var profile = sl.get_querystring_value("profile") ;
	   	if ( !profile ) {
	    	profile = "cee8ea07-e160-11e7-b884-1b54ec7f20bc"
	    }     

	    $.ajax({
			dataType: "json",
			url: "/cryptotickers",
			data: { profile : profile },
			success: function(obj) {
				sl.total_btc = obj.sum_total_btc;
				sl.total_eth = obj.sum_total_eth;
				sl.total_usd = obj.sum_total_usd;
				sl.total_sgd = obj.sum_total_sgd;
				sl.portfolio = obj.portfolio;	
				sl.profile_name = profile;
				sl.render_list();
			}
		});

	}

	






	//-------------
	this.get_querystring_value = function( name ) {

		var url = window.location.href;
		name = name.replace(/[\[\]]/g, "\\$&");
		var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)");
		results = regex.exec(url);
		if (!results) { 
			return null;
		}
		if (!results[2]) { 
			return '';
		}
		return decodeURIComponent(results[2].replace(/\+/g, " "));
	}


	//--------
	this.sprintf = function( ) {
		
		var str = arguments[0];
		for ( var i = 1 ; i < arguments.length ; i++ ) {
			str = str.replace("%s", arguments[i]);
		}
		return str;
	}


	//-----
	this.render_list = function() {
		
		console.log("render_list");

		var sl = this;

		
		var mylist = document.getElementById("threadindex_list");
		var str = ""

		if ( typeof sl.total_usd != "undefined" ) {
			str += "<li id='li_profile'>";
			str += "<div>";
			str += this.sprintf( "<div class='profile_header'>%s</div>", sl.profile_name );
			str += this.sprintf( "<div class='curr_rate_holding'>Total USD: <br/>%s </div>", this.numberWithCommas( sl.total_usd.toFixed(2) ));
			str += this.sprintf( "<div class='curr_rate_holding'>Total SGD: <br/>%s </div>", this.numberWithCommas( sl.total_sgd.toFixed(2) ));
			str += this.sprintf( "<div class='curr_rate_holding'>Total BTC: <br/>%s </div>", this.numberWithCommas( sl.total_btc.toFixed(4) ));
			str += this.sprintf( "<div class='curr_rate_holding'>Total ETH: <br/>%s </div>", this.numberWithCommas( sl.total_eth.toFixed(4) ));
			str += "</div>";
			str += "</li>";
		}
			

		for ( i = 0 ; i < sl.portfolio.length ; i++ ) {
			
			str += "<li>";

				var sl_obj 		= sl.portfolio[i];
				var quote 		= "BTC";
				if ( sl_obj.base == "BTC" || sl_obj.base == "ETH" ) {
					quote = "USDT";
				}

				var chart_url 	= this.sprintf("http://tradingview.com/e?symbol=%s%s", sl_obj.base , quote );	
				
				str += "<div class='curr_rate_header'>"
					str += this.sprintf( "<div class='curr_rate_symbol'><a href='%s' target='_blank'>%s</a></div>", chart_url, sl_obj.base );

				str += "</div>"
				str += "<div class='curr_rate'>";
					str += this.sprintf("<div class='curr_rate_inner'>%s USD</div>", sl_obj.usd.toFixed(4) );
					str += this.sprintf("<div class='curr_rate_inner'>%s BTC</div>", sl_obj.btc.toFixed(8) );
					str += this.sprintf("<div class='curr_rate_inner'>%s SGD</div>", sl_obj.sgd.toFixed(4) );
					str += this.sprintf("<div class='curr_rate_inner'>%s ETH</div>", sl_obj.eth.toFixed(8) );
					
				str += "</div>";
				
				if ( typeof sl_obj.total_usd != "undefined" ) {
					str += "<div>";
					str += this.sprintf( "<hr /><div class='curr_rate_holding_title'>You Own:  %s %s</div>", sl_obj.own, sl_obj.base );
					str += this.sprintf( "<div class='curr_rate_holding' id='curr_rate_holding_usd_%s'>%s USD</div>", sl_obj.base, this.numberWithCommas( sl_obj.total_usd.toFixed(2) ) );
					str += this.sprintf( "<div class='curr_rate_holding' id='curr_rate_holding_sgd_%s'>%s SGD</div>", sl_obj.base, this.numberWithCommas( sl_obj.total_sgd.toFixed(2) ) );
					str += this.sprintf( "<div class='curr_rate_holding' id='curr_rate_holding_btc_%s'>%s BTC</div>", sl_obj.base, this.numberWithCommas( sl_obj.total_btc.toFixed(4) ) );
					str += this.sprintf( "<div class='curr_rate_holding' id='curr_rate_holding_eth_%s'>%s ETH</div>", sl_obj.base, this.numberWithCommas( sl_obj.total_eth.toFixed(4) ) );
					str += "</div>"
				}
			str += "</li>";

		}
		


		mylist.innerHTML = str;
	}




	//-------------
	this.compare = function( a, b) {

		if ( a.total_usd < b.total_usd ) {
	    	return 1;
	    }
		if ( a.total_usd > b.total_usd ) {
			return -1;
		}
		return 0;
	
	}


	

	//--------------
	this.numberWithCommas = function(x) {
    	var parts = x.toString().split(".");
    	parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    	return parts.join(".");
	}

	//-------------
	this.init = function() {
		this.get_exchange_rates();

	}

}

document.addEventListener("DOMContentLoaded", function() {
	sl = new SimpleList();
	sl.init();
});

