/* Generated from Claude */


function PasswordViewModel (data){

    var self = this;


    self.secret_key = ko.observable();
    self.key = ko.observable();
	self.computed_password = ko.observable();


    self.compute_password = () =>{
		self.hmacSHA256(self.key(), self.secret_key()).then(
			hash => self.computed_password(hash));
    }

    self.reset_password = () =>{
        self.secret_key(undefined);
        self.key(undefined);
        self.computed_password(undefined);
    }


	self.hmacSHA256 = async (message, secretKey) => {
      const encoder = new TextEncoder();

	  const key = await crypto.subtle.importKey(
		'raw',
		encoder.encode(self.secret_key()),
		{ name: 'HMAC', hash: 'SHA-256' },
		false,
		['sign']
	  );

	  const signature = await crypto.subtle.sign(
		'HMAC',
		key,
		encoder.encode(message)
	  );

	  return Array.from(new Uint8Array(signature))
		.map(b => b.toString(16).padStart(2, '0'))
		.join('');
	}

};
