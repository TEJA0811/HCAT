import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ValidationPipe } from '@nestjs/common';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true, // removes extra properties
      forbidNonWhitelisted: true, // throw error if extra properties
      transform: true, // convert payload to DTO class instance
    }),
  );

  await app.listen(process.env.PORT ?? 3000);
}
bootstrap();
