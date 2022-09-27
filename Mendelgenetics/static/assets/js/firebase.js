document.getElementById("text_message").addEventListener("keydown", function (e) 
{
	if (e.key === "Enter") 
	{  
		send_message();
	}
});


async function showMessages(receiver_email, sender_email, support_id)
{
	console.log(receiver_email, sender_email);
	messages_list = ""
	$('#chat-messages').html("");
	
	const ref_1 = await db.collection("ChatMessages").where('sender_email', '==',  sender_email).where('receiver_email', '==', receiver_email).where('support_id', '==', support_id).get();
		
	
	const ref_2 = await db.collection("ChatMessages").where('sender_email', '==', receiver_email).where('receiver_email', '==',  sender_email).where('support_id', '==', support_id).get();
	
	if (ref_1.empty){
		db.collection("ChatMessages").where('sender_email', '==', receiver_email).where('receiver_email' , '==',  sender_email).where('support_id', '==', support_id)
		.onSnapshot(function(querySnapshot) {  
				includeMetadataChanges: true;
				querySnapshot.forEach(function(doc) {
				doc.data()['message'].forEach(function(messages)
				{
					if( messages['sender_email'] == receiver_email )
					{
						messages_list += `<div class="message">
							<div class="bubble">
								${messages['message']}
								<div class="corner"></div>
								<span class="left-time">${messages['date']} | ${messages['time'].replace(/:\d+ (\w\w)$/, ' $1')}</span>
							</div>
						</div>`;

					}
					
					else if ( messages['sender_email'] == sender_email ) 
					{
						messages_list += `<div class="message right">
							<div class="bubble">
								${messages['message']}
								<div class="corner"></div>
								<span class="right-time">${messages['date']} | ${messages['time'].replace(/:\d+ (\w\w)$/, ' $1')}</span>
							</div>
						</div>`;
					}
				
			
				});
				$('#chat-messages').html("");
				$('#chat-messages').html(messages_list);
				messages_list = ""
		
			
				// var height=$(".chat-message").height()+200;
				$('#chat-messages').scrollTop($('#chat-messages')[0].scrollHeight);
			});
		});
		
		}
	
	
	else
	{
		db.collection("ChatMessages").where('sender_email', '==',  sender_email).where('receiver_email', '==', receiver_email).where('support_id', '==', support_id)
		.onSnapshot(function(querySnapshot) {
				includeMetadataChanges: true;
				querySnapshot.forEach(function(doc) {
				doc.data()['message'].forEach(function(messages){
				if( messages['sender_email'] == sender_email ){

					messages_list += `<div class="message right">
						<div class="bubble">
							${messages['message']}
							<div class="corner"></div>
							<span class="right-time">${messages['date']} | ${messages['time'].replace(/:\d+ (\w\w)$/, ' $1')}</span>
						</div>
					</div>`;

				}   
				
				else if ( messages['sender_email'] == receiver_email ) {
					
					messages_list += `<div class="message">
						<div class="bubble">
							${messages['message']}
							<div class="corner"></div>
							<span class="left-time">${messages['date']} | ${messages['time'].replace(/:\d+ (\w\w)$/, ' $1')}</span>
						</div>
					</div>`;
				}
				
			});
			
			
			$('#chat-messages').html("");
			$('#chat-messages').html(messages_list);
			messages_list = ""


			
		});
		$('#chat-messages').scrollTop($('#chat-messages')[0].scrollHeight);
	
	});
	
	}

}



async function send_message()
{
	var receiver_name = $("#receiver_user_name").val();
	var receiver_email = $("#receiver_email").val();
	var support_id = $("#support_id").val();
	
	var sender_name = $("#sender_name").val();
	var sender_email = $("#sender_email").val();
	var support_subject = $("#support_subject").val();
	var support_date = $("#support_date").val();
	
	
	var message = $("#text_message").val();
	
	if (message == "")
	{
		$("#text_message").focus();
	}
	else
	{
		var sender_seen = 0;
		var reciver_seen = 0;
		
		var reciver_profile = "";
		var key = "";
		
		var file_type = "text";
		
		var today = new Date();
		var date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
		var time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
		var dateTime = date+' '+time;
		
		
		var message_date = new Date().toLocaleDateString('en-GB');
		var message_time = new Date().toLocaleTimeString();

		var chat_messages1 = db.collection("ChatMessages").where('sender_email', '==', sender_email).where('receiver_email', '==', receiver_email).where('support_id', '==', support_id)
		
		var chat_messages2 = db.collection("ChatMessages").where('sender_email', '==', receiver_email).where('receiver_email', '==', sender_email).where('support_id', '==', support_id)
		
		message_data = {
					date : message_date,
					file_type :"text",
					key : "",
					message : message,
					sender_email : sender_email,
					time : message_time,
				}
				
		let chat_messages1_obj = await chat_messages1.get();
		
		let chat_messages2_obj = await chat_messages2.get();
		
		
		if (chat_messages1_obj.empty && chat_messages2_obj.empty ) 
		{
			db.collection("ChatMessages").add({
				date_time : dateTime,
				
				message : [message_data],
				
				receiver : receiver_name,
				receiver_email : receiver_email,
				
				receiver_profile : "",
				receiver_seen : 1,
				
				sender : sender_name,
				sender_email : sender_email,

				support_id : support_id,
				support_subject : support_subject,
				support_date : support_date,
				status : "Open",
				
				sender_profile :"" ,
				sender_seen : 0,
			})
			.then(function(docRef) {
				console.log("Document written with ID: ", docRef);
			})
			.catch(function(error) {
				console.error("Error adding document: ", error);
			});
		
		}
		else
		{
			const increment = firebase.firestore.FieldValue.increment(1);
			var doc_id = "";
			
			const ref_1 = await db.collection("ChatMessages").where('sender_email', '==', sender_email).where('receiver_email', '==', receiver_email).where('support_id', '==', support_id).get();
			
			const ref_2 = await db.collection("ChatMessages").where('sender_email', '==', receiver_email).where('receiver_email', '==', sender_email).where('support_id', '==', support_id).get();
		
			if (ref_1.empty) 
			{
				const docRefId = ref_2.docs[0].id;
		
				db.collection("ChatMessages").doc(docRefId).update({
					message : firebase.firestore.FieldValue.arrayUnion(message_data),
					sender_seen : increment
				
				})
			}
			else
			{
				const docRefId = ref_1.docs[0].id;
			
				db.collection("ChatMessages").doc(docRefId).update({
					message : firebase.firestore.FieldValue.arrayUnion(message_data),
					receiver_seen : increment
				})
			}
		}

		$('#text_message').val("");
	
		showMessages(receiver_email, sender_email, support_id);
		// if (usertype == "Driver" )
		// {
		// 	$(".chat-active").find(".customerviewmessage").click();
		// }
		// else
		// {
		// 	$(".chat-active").find(".viewmessge").click();
		// }
	}
}



async function clear_notification_count(support_id, user_type)
{
	const ref = await db.collection("ChatMessages").where('support_id', '==', support_id).get()
	.then(function(querySnapshot) 
	{
		querySnapshot.forEach(function(doc) 
		{
			if (user_type == 'Admin')
			{
				doc.ref.update({receiver_seen: 0});
			}
			else
			{
				doc.ref.update({sender_seen: 0}) ;
			}
		});
	})
}
function show_msg(support_id)
{
	$.ajax({
		url: "/close_support_ticket/",
		method:'POST',
		cache: false,
		data: {'support_id':support_id},
		success: function (resp_data) 
		{
			$('#overlayer_transparent').hide();
			swal({
				icon:"warning",
				text:"Ticket closed successfully...",
				buttons: "Ok",
				dangerMode: true,
				closeOnClickOutside:false	
			}).then((willUpdate) => {
				location.reload();
			});
		}
	});
}

async function close_support_ticket_firestore(support_id)
{
	const ref = await db.collection("ChatMessages").where('support_id', '==', support_id).get()
	.then(function(querySnapshot) 
	{
		querySnapshot.forEach(function(doc) 
		{
			doc.ref.update({status: "Close"}).then(function() {
				show_msg(support_id);
			});
		});
	});
}

function close_support_ticket(support_id)
{
	swal({
		icon:"warning",
		text:"Are you sure, to close the support ticket ?",
		buttons: ["No", "Yes"],
		dangerMode: true,
		closeOnClickOutside:false	
	}).then((willUpdate) => 
	{
		
		if(willUpdate) {
			$('#overlayer_transparent').show();
			close_support_ticket_firestore(support_id);
		}
	});
}