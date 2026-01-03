import { Seeder } from 'typeorm-extension';
import { DataSource } from 'typeorm';
import { User } from '../../users/entities/user.entity';

export class UserSeeder implements Seeder {
  async run(dataSource: DataSource): Promise<void> {
    const repo = dataSource.getRepository(User);

    await repo.insert([
      {
        name: 'Test User 1',
        email: 'user1@example.com',
      },
      {
        name: 'Test User 2',
        email: 'user2@example.com',
      },
    ]);
  }
}
