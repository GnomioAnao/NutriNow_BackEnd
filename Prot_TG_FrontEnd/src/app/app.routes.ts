import { Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { CadastroComponent } from './cadastro/cadastro.component';
import { HomeComponent } from './home/home.component';
import { ChatbotComponent } from './chatbot/chatbot.component';

export const routes: Routes = [
    {path: 'login', component: LoginComponent},
    {path: 'cadastro', component: CadastroComponent},
    {path: 'home', component: HomeComponent},
    {path: 'chatbot', component: ChatbotComponent},
    { path: '', redirectTo: 'home', pathMatch: 'full' } // testando essa parada
];
