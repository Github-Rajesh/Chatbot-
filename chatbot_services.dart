import 'dart:convert';
import 'package:http/http.dart' as http;
class ChatService {
 static const String apiUrl = 'http://192.168.0.186:5000/';
 Future<Map<String, dynamic>> sendMessage(String message) async {
   final response = await http.post(
     Uri.parse(apiUrl),
     headers: {'Content-Type': 'application/json'},
     body: jsonEncode({'question': message}),
   );
   if (response.statusCode == 200) {
     return jsonDecode(response.body);
   } else {
     throw Exception('Failed to load chatbot response');
   }
 }
}